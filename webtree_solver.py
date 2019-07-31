import csv
import os
import click

from ortools.sat.python import cp_model


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


def get_course_weight(pos, is_exp):
    if pos is None:
        return -1
    if (is_exp):
        return 2**(5 - pos)
    else:
        if pos == 1:
            return 10
        if pos == 2:
            return 9
        if pos == 3:
            return 8
        if pos == 4:
            return 2
        if pos == 5:
            return 1
    return -1


def get_period(word):
    period = word.split()[0]
    if period == 'P1':
        return 1
    if period == 'P2':
        return 2
    if period == 'P3':
        return 3
    if period == 'P4':
        return 4
    return -1


def get_num_stars(rank):
    if rank is None:
        return "UH-OH"
    ret = ""
    for i in range(0, rank):
        ret += '*'
    return ret


def read_data(filename, is_exp):
    count = 0
    course_hashes_to_names = {}
    students = []
    full_mapping = {}
    students_to_picks = {}
    student_hashes_to_names = {}

    courses = []

    num_courses_per_period = [0, 0, 0, 0]
    first_line = []

    student_course_to_student_rank = {}

    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')

        for line in csv_reader:
            # Read in first line of courses
            if count == 0:
                first_line = line
                count += 1
                for i in range(3, len(line)):
                    if (len(line[i]) < 3):
                        continue
                    num_courses_per_period[get_period(line[i]) - 1] += 1
                    course_hashes_to_names.update({hash(line[i]): line[i]})
                    courses.append(hash(line[i]))
                continue
            # Get the full student
            full_student = (line[0], line[1], line[2])
            student_id = hash(full_student)
            student_hashes_to_names.update({student_id: full_student})
            students.append(student_id)

            count += 1
            # if count > 3:
            #     break
            periods = []
            index_in_line = 3
            for period in range(1, 5):
                picks = []
                for course in range(0, num_courses_per_period[period - 1]):
                    pick_rank = None
                    if (line[index_in_line] != ''):
                        pick_rank = int(line[index_in_line])
                    weight = get_course_weight(pick_rank, is_exp)
                    full_mapping.update({
                        (hash(first_line[index_in_line]), student_id):
                        weight
                    })
                    student_course_to_student_rank.update({
                        (hash(first_line[index_in_line]), student_id):
                        pick_rank
                    })
                    if weight != -1:
                        picks.append(hash(first_line[index_in_line]))
                    index_in_line += 1
                periods.append(picks)
            students_to_picks.update({student_id: periods})

        # for c in course_hashes_to_names:
        #     for s in students:
        #         if (c, s) not in full_mapping:
        #             full_mapping.update({(c, s): -100})

        return (course_hashes_to_names, courses, students, full_mapping,
                students_to_picks, student_hashes_to_names,
                student_course_to_student_rank)


@click.command()
@click.option(
    '--exp_weighting',
    '-e',
    default=None,
    help='Whether or not you want to use the exponential weighting scheme')
def main(exp_weighting):
    exponential_weighting = False
    if (exp_weighting is not None):
        exponential_weighting = True

    data_path = 'AutomatedCoursePicks.csv'  #Data directory
    parsed_data = read_data(data_path, exponential_weighting)
    course_hashes_to_names = parsed_data[0]
    courses = parsed_data[1]
    students = parsed_data[2]
    mapping = parsed_data[3]
    students_to_picks = parsed_data[4]
    student_hashes_to_names = parsed_data[5]
    student_course_to_student_rank = parsed_data[6]

    model = cp_model.CpModel()
    course_match = {}

    for c in courses:
        for s in students:
            course_match[(c, s)] = model.NewBoolVar(
                'course%iis assigned to %i' % (c, s))

    for c in courses:
        for s in students:
            if student_course_to_student_rank[(c, s)] is None:
                model.Add(course_match[(c, s)] == 0)

    for s in students_to_picks:
        for period in range(0, 4):
            picks = students_to_picks[s][period]
            if (len(picks) != 0):
                model.Add(sum(course_match[(c, s)] for c in picks) == 1)

    for c in courses:
        course_max = 10
        course_min = 5
        model.Add(sum(course_match[(c, s)] for s in students) <= course_max)
        model.Add(sum(course_match[(c, s)] for s in students) >= course_min)

    model.Maximize(
        sum(course_match[(c, s)] * mapping[(c, s)] for c in courses
            for s in students))

    solver = cp_model.CpSolver()

    solver.Solve(model)

    # Log statistics about the solution. Used to evaluate the "goodness" of a solution
    num_students = len(students)

    if not os.path.exists('results'):
        os.mkdir('results')

    cur_filename = 'results/' + 'results.csv'  #+ str(datetime.datetime.now())
    f = open(cur_filename, 'w')

    # for s in students_to_picks:
    #     for period in range(0, 4):
    #         picks = students_to_picks[s][period]
    #         for c in picks:
    #             if solver.Value(course_match[(c, s)]) == 1:
    #                 print("Course: " + str(c) + " Student: " +
    #                       str(student_hashes_to_names[s]))

    #         print(sum(solver.Value(course_match[(c, s)]) for c in picks))

    for student_hash in student_hashes_to_names:
        student_name = student_hashes_to_names[student_hash]
        str_to_write = student_name[0] + ',' + student_name[
            1] + ',' + student_name[2] + ','
        for c in courses:
            if solver.Value(course_match[(c, student_hash)]) == 1:
                # print(course_match[(c, student_hash)])
                str_to_write += course_hashes_to_names[c]
                str_to_write += get_num_stars(
                    student_course_to_student_rank[(c, student_hash)])
                str_to_write += ', '
        str_to_write += '\n'
        f.write(str_to_write)
    # f.write("\n=================")
    # f.write(
    #     "\nPercent of all students that got their {}th choice: {}% ({} total)\n"
    #     .format(i + 1, percent, num_successes[i]))
    # f.write(
    #     "\nPercent of seniors that got their {}th choice: {}% ({} total)".
    #     format(i + 1, senior_percent, num_senior_succ[i]))
    # f.write(
    #     "\nPercent of juniors that got their {}th choice: {}% ({} total)".
    #     format(i + 1, junior_percent, num_junior_succ[i]))
    # f.write(
    #     "\nPercent of sophomores that got their {}th choice: {}% ({} total)"
    #     .format(i + 1, soph_percent, num_soph_succ[i]))
    # f.write(
    #     "\nPercent of first years that got their {}th choice: {}% ({} total)"
    #     .format(i + 1, first_percent, num_first_succ[i]))
    # f.write("\n=================\n")
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
