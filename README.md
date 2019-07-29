####Course Assignment

A project that assigns courses to students using weighted maximum satisfiability techniques in an effort to maximize utility.  It guarantees that, should such a solution exist, each course will have at minimum 5 students and at most 10 and that students will not receive courses that they have not requested.  It offers two objective functions that give preference to students first picks over their second picks and so on and so forth.  

## Getting Started

This project is written in python3 and depends on click and Google's ortools.  To install the two libraries on Mac or Linux, open a terminal.  

You should have pip automatically installed with python but if you don't, run the command on linux:

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
On 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Aidan O'Neill** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Much thanks to the devs at Google for their ortools library

