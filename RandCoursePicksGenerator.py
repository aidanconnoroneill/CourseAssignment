import random
import string


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def main():

    cur_filename = 'AutomatedCoursePicks.csv'
    f = open(cur_filename, 'w')
    so_far = []
    for i in range(0, 160):
        so_far.clear()
        f.write(randomString())
        f.write(',')
        for period in range(0, 4):
            for course_pick in range(0, 5):
                while (True):
                    course = random.randint(0, 20)
                    if course not in so_far:
                        so_far.append(course)
                        break
                course += 20 * period
                f.write(str(course))
                f.write(',')
        f.write('\n')

    f.close()


if __name__ == "__main__":
    main()