*** Settings ***
Documentation    meditation backend testsuite
Suite Setup      Set Variables

*** Keywords ***
Set Variables
  Set Suite Variable    ${BACKEND_URL}  http://localhost:6000  children=true
