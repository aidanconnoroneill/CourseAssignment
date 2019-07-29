import csv
import os
import click
import datetime

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


def read_data(filename, is_exp):
    count = 0
    courses = []
    students = []
    full_mapping = {}
    students_to_picks = {}
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file, delimiter=',')

        for line in csv_reader:
            if count == 0:
                count += 1
                continue
            count += 1
            if count > 300:
                break
            student_id = hash(line[0])
            students.append(student_id)
            periods = []
            for period in range(1, 5):
                picks = []
                for pick_index in range(1, 6):
                    index = (period - 1) * 5 + pick_index
                    course_id = int(line[index])
                    weight = get_course_weight(pick_index, is_exp)
                    full_mapping.update({(course_id, student_id): weight})
                    if (course_id not in courses):
                        courses.append(course_id)
                    picks.append(course_id)
                periods.append(picks)
            students_to_picks.update({student_id: periods})

        for c in courses:
            for s in students:
                if (c, s) not in full_mapping:
                    full_mapping.update({(c, s): 0})
        return (courses, students, full_mapping, students_to_picks)


@click.command()
# @click.argument('data', default='CoursePicks')
@click.option(
    '--exp_weighting',
    '-e',
    default=None,
    help='Whether or not you want to use the exponential weighting scheme')
def main(exp_weighting):
    exponential_weighting = False
    if (exp_weighting is not None):
        exponential_weighting = True

    data_path = 'CoursePicks.csv'  # append data directory
    parsed_data = read_data(data_path, exponential_weighting)
    courses = parsed_data[0]
    students = parsed_data[1]
    mapping = parsed_data[2]
    students_to_picks = parsed_data[3]
    print('Parsed')
    print(students_to_picks)
    model = cp_model.CpModel()
    course_match = {}

    for c in courses:
        for s in students:
            course_match[(c, s)] = model.NewBoolVar(
                'course%iis assigned to %i' % (c, s))

    for s in students_to_picks:
        for period in range(0, 4):
            picks = students_to_picks[s][period]
            model.Add(sum(course_match[(c, s)] for c in picks) == 1)
    for c in courses:
        course_max = 10
        course_min = 5
        model.Add(sum(course_match[(c, s)] for s in students) <= course_max)
        # model.Add(sum(course_match[(c, s)] for s in students) >= course_min)

    # model.Maximize(
    #     sum(course_match[(c, s)] * webtree[(c, s)]) for c in courses
    #     for s in students)
    model.Maximize(
        sum(course_match[(c, s)] * mapping[(c, s)] for c in courses
            for s in students))

    solver = cp_model.CpSolver()
    # solution_printer = ClassesPartialSolutionPrinter(course_match, courses,
    # students, range(5))
    solver.Solve(model)

    # Log statistics about the solution. Used to evaluate the "goodness" of a solution
    num_students = len(students)

    if not os.path.exists('results'):
        os.mkdir('results')

    cur_filename = 'results/' + '_' + str(datetime.datetime.now())
    f = open(cur_filename, 'w')
    # for i in range(0, 25):
    # percent = (num_successes[i] * 100 / num_students)
    # senior_percent = (num_senior_succ[i] * 100 / tot_num_senior)
    # junior_percent = (num_junior_succ[i] * 100 / tot_num_junior)
    # soph_percent = (num_soph_succ[i] * 100 / tot_num_soph)
    # first_percent = (num_first_succ[i] * 100 / tot_num_first)

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
