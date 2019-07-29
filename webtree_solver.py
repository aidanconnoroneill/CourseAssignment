import sys
import csv
import os
import click
import datetime
from ortools.sat.python import cp_model

tot_num_senior = 0
tot_num_junior = 0
tot_num_soph = 0
tot_num_first = 0

# Percent of students that got course x
# 65
# 68
# 71
# 65
# 57
# 65
# 57
# 45
# 61
# 62
# 52
# 51
# 54
# 43
# 38
# 53
# 52
# 39
# 44
# 42
# 31
# 31
# 24
# 18
# 12

t_weights_dict = dict()
t_weights_dict.update({1: 15, 2: 14, 3: 13, 4: 13, 5: 12, 6: 12, 7: 11})
for i in range(8, 22):
    t_weights_dict.update({i: t_weights_dict[i - 7] - 1})
t_weights_dict.update({22: 12})
for i in range(23, 26):
    t_weights_dict.update({i: t_weights_dict[i - 1] - 1})


class ClassesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, course_assignments, courses, students, sols):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._course_assignments = course_assignments
        self._students = students
        self._courses = courses
        self._solutions = set(sols)
        self._solution_count = 0

    def OnSolutionCallback(self):
        self._solution_count += 1
        if self._solution_count in self._solutions:
            print('Solution %i' % self._solution_count)
            for s in self._students:
                for c in self._courses:
                    if self.Value(self._course_assignments[(c, s)]):
                        print('  Student %i has class %i' % (s, c))
            self.StopSearch()

    def solution_count(self):
        return self._solution_count


def get_webtree_weight(tree, branch, student_class, is_major, is_major_2):
    ret = 25 - ((tree - 1) * 7 + branch - 1)
    ret = t_weights_dict[26 - ret]

    if student_class == 'SENI':
        ret *= 4
    if student_class == 'JUNI':
        ret *= 3
    if student_class == 'SOPH':
        ret *= 2
    else:
        ret *= 1

    if is_major:
        ret *= 1
    if is_major_2:
        ret *= 1

    return int(ret)


def read_data(filename):
    global tot_num_senior
    global tot_num_junior
    global tot_num_soph
    global tot_num_first

    webtree = {}
    courses = {}
    students = {}
    count = 0
    full_web = {}
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')

        for line in csv_reader:
            if count == 0:
                count += 1
                continue
            student_id = int(line[0])
            if student_id not in students:
                student_class = line[1]

                if student_class == 'SENI':
                    tot_num_senior += 1
                elif student_class == 'JUNI':
                    tot_num_junior += 1
                elif student_class == 'SOPH':
                    tot_num_soph += 1
                else:
                    tot_num_first += 1

                major = line[6]
                major_2 = line[7]
                students.update({student_id: (student_class, major, major_2)})
            course_id = int(line[2])
            if course_id not in courses:
                course_ceiling = int(line[5])
                course_subject = line[8]
                course_number = line[9]
                course_section = line[10]
                courses.update({
                    course_id: (course_ceiling, course_subject, course_number,
                                course_section)
                })

            tree_num = int(line[3])
            branch = int(line[4])
            is_maj = False
            if students[student_id][1] == courses[course_id][1]:
                is_maj = True

            is_maj_2 = False
            if students[student_id][1] == courses[course_id][2]:
                is_maj_2 = True

            weight = get_webtree_weight(
                tree_num, branch, students[student_id][0], is_maj, is_maj_2)
            if (course_id, student_id
                ) not in webtree or webtree[(course_id, student_id)] < weight:
                webtree.update({(course_id, student_id): weight})
            if student_id not in full_web:
                full_web.update({student_id: [0] * 25})
            full_web[student_id][(tree_num - 1) * 7 + branch - 1] = course_id
            # web_rep = webtree[student_id]
            # web_rep[get_webtree_pos(tree_num, branch)] = course_id
            # webtree.update({student_id: web_rep})
            # webtree.append((student_id, course_id, tree_num, branch))
        for c in courses:
            for s in students:
                if (c, s) not in webtree:
                    webtree.update({(c, s): 0})
        return (courses, students, webtree, full_web)


@click.command()
@click.argument('data', default='spring-2015')
def main(data):

    data_path = 'WebTree Data/' + data + '.csv'  # append data directory
    parsed_data = read_data(data_path)
    courses = parsed_data[0]
    students = parsed_data[1]
    webtree = parsed_data[2]
    full_web = parsed_data[3]
    print 'parsed'
    model = cp_model.CpModel()
    course_match = {}

    for c in courses:
        for s in students:
            course_match[(c, s)] = model.NewBoolVar(
                'course%iis assigned to %i' % (c, s))

    for s in students:
        model.Add(sum(course_match[(c, s)] for c in courses) > 2)
        model.Add(sum(course_match[(c, s)] for c in courses) < 5)

    for c in courses:
        max = courses[c][0]
        model.Add(sum(course_match[(c, s)] for s in students) <= max)

    # model.Maximize(
    #     sum(course_match[(c, s)] * webtree[(c, s)]) for c in courses
    #     for s in students)
    model.Maximize(
        sum(course_match[(c, s)] * webtree[(c, s)] for c in courses
            for s in students))

    solver = cp_model.CpSolver()
    # solution_printer = ClassesPartialSolutionPrinter(course_match, courses,
    # students, range(5))
    solver.Solve(model)

    # Log statistics about the solution. Used to evaluate the "goodness" of a solution
    num_successes = [0] * 25
    num_senior_succ = [0] * 25
    num_junior_succ = [0] * 25
    num_soph_succ = [0] * 25
    num_first_succ = [0] * 25

    for s in students:
        for i in range(0, 25):
            c = full_web[s][i]
            # print(course_match[(c, s)])
            if c != 0 and solver.Value(course_match[(c, s)]) == 1:
                num_successes[i] += 1

                cur_student = students[s]
                if cur_student[0] == 'SENI':
                    num_senior_succ[i] += 1
                elif cur_student[0] == 'JUNI':
                    num_junior_succ[i] += 1
                elif cur_student[0] == 'SOPH':
                    num_soph_succ[i] += 1
                elif cur_student[0] == 'FRST':
                    num_first_succ[i] += 1

    num_students = len(full_web)

    if not os.path.exists('results'):
        os.mkdir('results')

    cur_filename = 'results/' + data + '_' + str(datetime.datetime.now())
    f = open(cur_filename, 'w')
    for i in range(0, 25):
        percent = (num_successes[i] * 100 / num_students)
        senior_percent = (num_senior_succ[i] * 100 / tot_num_senior)
        junior_percent = (num_junior_succ[i] * 100 / tot_num_junior)
        soph_percent = (num_soph_succ[i] * 100 / tot_num_soph)
        first_percent = (num_first_succ[i] * 100 / tot_num_first)

        f.write("\n=================")
        f.write(
            "\nPercent of all students that got their {}th choice: {}% ({} total)\n".
            format(i + 1, percent, num_successes[i]))
        f.write(
            "\nPercent of seniors that got their {}th choice: {}% ({} total)".
            format(i + 1, senior_percent, num_senior_succ[i]))
        f.write(
            "\nPercent of juniors that got their {}th choice: {}% ({} total)".
            format(i + 1, junior_percent, num_junior_succ[i]))
        f.write(
            "\nPercent of sophomores that got their {}th choice: {}% ({} total)".
            format(i + 1, soph_percent, num_soph_succ[i]))
        f.write(
            "\nPercent of first years that got their {}th choice: {}% ({} total)".
            format(i + 1, first_percent, num_first_succ[i]))
        f.write("\n=================\n")
    f.close()
    print('Done writing')

    # solver.SearchForAllSolutions(model, solution_printer)
    # Statistics.
    print('Results saved to {}'.format(cur_filename))
    print()
    print('Statistics')
    print('  - conflicts       : %i' % solver.NumConflicts())
    print('  - branches        : %i' % solver.NumBranches())
    print('  - Value of courses = %i' % solver.ObjectiveValue())

    print('  - wall time       : %f s' % solver.WallTime())
    # print('  - solutions found : %i' % solution_printer.solution_count())

    # x = solver.NumVar(-solver.infinity(), solver.infinity(), 'x')


if __name__ == "__main__":
    main()
