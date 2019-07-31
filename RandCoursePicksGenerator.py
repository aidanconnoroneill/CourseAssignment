import random
import string


def randomString(stringLength=5):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def getCourseNumbers(period):
    opts = [-1, -1, 1, 2, 3, 4, 5]
    if period == 2:
        opts = [-1, -1, -1, 1, 2, 3, 4, 5]
    random.shuffle(opts)
    return opts


def main():

    cur_filename = 'AutomatedCoursePicks.csv'
    f = open(cur_filename, 'w')
    so_far = []
    for i in range(0, 75):
        so_far.clear()
        f.write(randomString())
        f.write(',')
        f.write(randomString())
        f.write(',')
        f.write(str(random.randint(0, 5)))
        f.write(',')
        teach_for_period = random.randint(0, 3)
        for i in range(0, 4):
            picks = getCourseNumbers(i)
            if i == teach_for_period:
                for j in range(0, len(picks)):
                    f.write(',')
            else:
                for j in range(0, len(picks)):
                    if picks[j] == -1:
                        f.write(',')
                    else:
                        f.write(str(picks[j]))
                        f.write(',')

        f.write('\n')

    f.close()


if __name__ == "__main__":
    main()