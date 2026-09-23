// =========================================================
// GET CHART DATA
// =========================================================

const chartDataElement = document.getElementById("chartData");

const chartData = chartDataElement
    ? JSON.parse(chartDataElement.dataset.chart)
    : [];

const gradeLabels = chartDataElement
    ? JSON.parse(chartDataElement.dataset.gradeLabels)
    : [];

const gradeData = chartDataElement
    ? JSON.parse(chartDataElement.dataset.gradeData)
    : [];

const passFailLabels = chartDataElement
    ? JSON.parse(chartDataElement.dataset.passFailLabels)
    : [];

const passFailData = chartDataElement
    ? JSON.parse(chartDataElement.dataset.passFailData)
    : [];


// =========================================================
// DASHBOARD
// =========================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard JS loaded");

    if (typeof Chart === "undefined") {

        console.error("Chart.js is not loaded!");

        return;
    }


    // =====================================================
    // PERFORMANCE OVERVIEW
    // =====================================================

    const performanceCanvas =
        document.getElementById("performanceChart");

    if (performanceCanvas) {

        new Chart(performanceCanvas, {

            type: "bar",

            data: {

                labels: [
                    "Python",
                    "DSA",
                    "DBMS",
                    "Web Development"
                ],

                datasets: [
                    {
                        label: "Average Marks",

                        data: chartData,

                        borderWidth: 1
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100

                    }

                }

            }

        });

    }


    // =====================================================
    // GRADE DISTRIBUTION
    // =====================================================

    const gradeCanvas =
        document.getElementById("gradeChart");

    if (gradeCanvas) {

        new Chart(gradeCanvas, {

            type: "bar",

            data: {

                labels: gradeLabels,

                datasets: [
                    {
                        label: "Number of Students",

                        data: gradeData,

                        borderWidth: 1
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        ticks: {
                            stepSize: 1
                        }

                    }

                }

            }

        });

    }


    // =====================================================
    // PASS / FAIL DISTRIBUTION
    // =====================================================

    const passFailCanvas =
        document.getElementById("passFailChart");

    if (passFailCanvas) {

        new Chart(passFailCanvas, {

            type: "doughnut",

            data: {

                labels: passFailLabels,

                datasets: [
                    {
                        label: "Students",

                        data: passFailData,

                        borderWidth: 1
                    }
                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false

            }

        });

    }


    // =====================================================
    // ATTENDANCE VS PERFORMANCE
    // =====================================================

    const attendancePerformanceElement =
        document.getElementById("attendancePerformanceData");

    const attendancePerformanceCanvas =
        document.getElementById("attendancePerformanceChart");

    if (attendancePerformanceElement && attendancePerformanceCanvas) {

        const attendancePerformanceData = JSON.parse(
            attendancePerformanceElement.dataset.points
        );

        new Chart(attendancePerformanceCanvas, {

            type: "scatter",

            data: {

                datasets: [
                    {
                        label: "Students",
                        data: attendancePerformanceData,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Attendance (%)"
                        },
                        min: 0,
                        max: 100
                    },

                    y: {
                        title: {
                            display: true,
                            text: "Performance / Percentage (%)"
                        },
                        min: 0,
                        max: 100
                    }

                },

                plugins: {

                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                return items.length
                                    ? items[0].raw.name
                                    : "";
                            },
                            label: function (context) {
                                return `Attendance: ${context.raw.x}% | Performance: ${context.raw.y}%`;
                            }
                        }
                    }

                }

            }

        });

    }


    // =====================================================
    // STUDY HOURS VS PERFORMANCE
    // =====================================================

    const studyHoursPerformanceElement =
        document.getElementById("studyHoursPerformanceData");

    const studyHoursPerformanceCanvas =
        document.getElementById("studyHoursPerformanceChart");

    if (studyHoursPerformanceElement && studyHoursPerformanceCanvas) {

        const studyHoursPerformanceData = JSON.parse(
            studyHoursPerformanceElement.dataset.points
        );

        new Chart(studyHoursPerformanceCanvas, {

            type: "scatter",

            data: {

                datasets: [
                    {
                        label: "Students",
                        data: studyHoursPerformanceData,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    x: {
                        type: "linear",
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Study Hours"
                        }
                    },

                    y: {
                        title: {
                            display: true,
                            text: "Performance / Percentage (%)"
                        },
                        min: 0,
                        max: 100
                    }

                },

                plugins: {

                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                return items.length
                                    ? items[0].raw.name
                                    : "";
                            },
                            label: function (context) {
                                return `Study Hours: ${context.raw.x} | Performance: ${context.raw.y}%`;
                            }
                        }
                    }

                }

            }

        });

    }


    // =====================================================
    // ASSIGNMENT SCORE VS PERFORMANCE
    // =====================================================

    const assignmentPerformanceElement =
        document.getElementById("assignmentPerformanceData");

    const assignmentPerformanceCanvas =
        document.getElementById("assignmentPerformanceChart");

    if (assignmentPerformanceElement && assignmentPerformanceCanvas) {

        const assignmentPerformanceData = JSON.parse(
            assignmentPerformanceElement.dataset.points
        );

        new Chart(assignmentPerformanceCanvas, {

            type: "scatter",

            data: {

                datasets: [
                    {
                        label: "Students",
                        data: assignmentPerformanceData,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Assignment Score (%)"
                        },
                        min: 0,
                        max: 100
                    },

                    y: {
                        title: {
                            display: true,
                            text: "Performance / Percentage (%)"
                        },
                        min: 0,
                        max: 100
                    }

                },

                plugins: {

                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                return items.length
                                    ? items[0].raw.name
                                    : "";
                            },
                            label: function (context) {
                                return `Assignment Score: ${context.raw.x}% | Performance: ${context.raw.y}%`;
                            }
                        }
                    }

                }

            }

        });

    }


    // =====================================================
    // PREVIOUS MARKS VS CURRENT PERFORMANCE
    // =====================================================

    const previousMarksPerformanceElement =
        document.getElementById("previousMarksPerformanceData");

    const previousMarksPerformanceCanvas =
        document.getElementById("previousMarksPerformanceChart");

    if (previousMarksPerformanceElement && previousMarksPerformanceCanvas) {

        const previousMarksPerformanceData = JSON.parse(
            previousMarksPerformanceElement.dataset.points
        );

        new Chart(previousMarksPerformanceCanvas, {

            type: "scatter",

            data: {

                datasets: [
                    {
                        label: "Students",
                        data: previousMarksPerformanceData,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    x: {
                        type: "linear",
                        title: {
                            display: true,
                            text: "Previous Marks (%)"
                        },
                        min: 0,
                        max: 100
                    },

                    y: {
                        title: {
                            display: true,
                            text: "Current Performance / Percentage (%)"
                        },
                        min: 0,
                        max: 100
                    }

                },

                plugins: {

                    tooltip: {
                        callbacks: {
                            title: function (items) {
                                return items.length
                                    ? items[0].raw.name
                                    : "";
                            },
                            label: function (context) {
                                return `Previous Marks: ${context.raw.x}% | Current Performance: ${context.raw.y}%`;
                            }
                        }
                    }

                }

            }

        });

    }


    // =====================================================
    // INDIVIDUAL STUDENT PERFORMANCE
    // =====================================================

    const studentAnalyticsElement =
        document.getElementById("studentAnalyticsData");

    const studentPerformanceCanvas =
        document.getElementById("studentPerformanceChart");

    if (studentAnalyticsElement && studentPerformanceCanvas) {

        const studentMarks = JSON.parse(
            studentAnalyticsElement.dataset.marks
        );

        new Chart(studentPerformanceCanvas, {

            type: "bar",

            data: {

                labels: [
                    "Python",
                    "DSA",
                    "DBMS",
                    "Web Development"
                ],

                datasets: [
                    {
                        label: "Marks (%)",
                        data: studentMarks,
                        borderWidth: 1
                    }
                ]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                scales: {

                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: "Marks (%)"
                        }
                    }

                }

            }

        });

    }

});
