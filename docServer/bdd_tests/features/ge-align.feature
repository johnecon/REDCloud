Feature: GE-Align
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to align graph elements
  So that usability and layout is improved
  
  Scenario: Align Top

  	Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "my_partner" swimlane
    And I "align-top" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "top alligned"
     | name             |
     | Test object      |
     | Test object 2    |

  Scenario: Align Bottom

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "my_partner" swimlane
    And I "align-bottom" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "bottom alligned"
     | name             |
     | Test object      |
     | Test object 2    |

  Scenario: Align Left

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "me" swimlane
    And I "align-left" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "left alligned"
     | name             |
     | Test object      |
     | Test object 2    |


  Scenario: Align Right

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "me" swimlane
    And I "align-right" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "right alligned"
     | name             |
     | Test object      |
     | Test object 2    |

  Scenario: Align Center X

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "me" swimlane
    And I "align-center-x" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "center-x alligned"
     | name             |
     | Test object      |
     | Test object 2    |

  Scenario: Align Center Y

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "me" swimlane
    And I "align-center-y" nodes
     | name             |
     | Test object      |
     | Test object 2    |
    Then nodes below should be "center-y alligned"
     | name             |
     | Test object      |
     | Test object 2    |

  Scenario: Distribute Vertically

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "me" swimlane
    And I create "Test object 3" "object" node in "me" swimlane
    And I "distribute-vertically" nodes
     | name             |
     | Test object      |
     | Test object 2    |
     | Test object 3    |
    Then nodes below should be "vertically distributed"
     | name             |
     | Test object      |
     | Test object 2    |
     | Test object 3    |