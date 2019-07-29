# Course Assignment

A project that assigns courses to students using weighted maximum satisfiability techniques in an effort to maximize utility.  It guarantees that, should such a solution exist, each course will have at minimum 5 students and at most 10 and that students will not receive courses that they have not requested.  It offers two objective functions that give preference to students first picks over their second picks and so on and so forth.  


### Prerequisites

This project is written in python3 and depends on click and Google's ortools.  To install the two libraries on Mac or Linux, open a terminal.  

You should have pip automatically installed with python but if you don't, run these commands on linux:

```
sudo apt update
sudo apt install python3-pip
```
For mac, run 
```
sudo easy_install pip
```
Once you've installed pip, run the following two commands:
```
pip3 install ortools
pip3 install click
```

## Getting Started

Once you have the dependencies outlined in Prerequisites, download webtree_solver.py and place it in the same directory as the csv you have stored the students' course perferences in.  Name your csv CoursePicks.csv.  An example csv is provided in AutomatedCoursePicks.csv above - it should have a header row, and each row afterwards should follow the format of 
```
Name, Period 1 Preference 1, Period 1 Preference 2, Period 1 Preference 3, Period 1 Preference 4, Period 1 Preference 5, Period 2 Preference 1, ...
```
Please note that if either the number of periods or number of preferences preferences change from 4 and 5 respectively, this code will not run properly.  

To run, open a terminal and navigate to the directory that contains webtree_solver.py.  To use the default configuration, run with:

```
python3 webtree_solver.py
```
If instead of using the default configuration, you wish to use the exponential weighting scheme, run with 

```
python3 webtree_solver.py -e 1
```

The default configuration gives a weighting scheme of 10, 9, 8, 2 and 1 to each of a student's first, second, third, fourth and fifth picks.  The exponential weighting scheme gives a weighting of 16, 8, 4, 2, and 1 to the picks.  

### Configuring

If you want to change the course ceiling and floor, go to the following two lines of code 

```
        course_max = 10
        course_min = 5
```
and change them to the values that you prefer.  Similarly, if you want to try a different weighting scheme, navigate to 

```
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
```
Edit the values after each "return" statement to whatever weight you prefer.  

## Authors

* **Aidan O'Neill** - *Initial work* - [Aidan](https://github.com/aidanoneill3776)

See also the list of [contributors](https://github.com/aidanoneill3776/CourseAssignment/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Much thanks to the devs at Google for their ortools library

