Feature: GE-Export
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to align graph elements
  So that usability and layout is improved

  Scenario: Object Import

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
    And I export "Test object" object node to "smthn"
    And I save
    Then I should see a save success message
    When I import "smthn" object node as "Imported Test object" in "my_partner" swimlane
    Then I should see "Importing smthn" "import action" node in "my_partner" swimlane
    And  I should see "Imported Test object" "object" node in "my_partner" swimlane
    When I save
    Then I should see a save success message

  Scenario: Objects Import

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
    And I export "Test object" and "Test object 2" object nodes to "smthn"
    And I save
    Then I should see a save success message
    When I import "smthn" object node as "Imported Test object" in "my_partner" swimlane
    Then I should see "Exporting Test object and Test object 2 into smthn" "external action" node in "me" swimlane
    Then  I should see "smthn" "object" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Template Import

    Given a set of specific users
     | username     | first_name                | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin            | admin                 | admin@admin.dk            | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com        | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    And "admin" sets "my project"`s graph as a template
    And a project "second project" created by "admin"
    And "me" contributes to "second project"
    And "my_partner" contributes to "second project"
    And "admin" exports "second project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    And I create "Test object 2" "object" node in "my_partner" swimlane
    And I save
    And I navigate to the graph editor of "second project"
    And I import "my project" template from "me" swimlane
    Then I should see "Test object" "object" node in "me" swimlane
    And  I should see "Test object 2" "object" node in "my_partner" swimlane
    When I save
    Then I should see a save success message