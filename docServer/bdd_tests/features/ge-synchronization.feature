Feature: GE-Synchronization
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to synchronize object and action nodes
  So that I realize them on parallel

  Scenario: Action Realization When Connected With Object

    Given a set of specific users
     | username     | first_name          | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin        | admin               | admin@admin.dk          | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com    | 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test action" "action" node in "me" swimlane
    And I create "Test object" "object" node in "me" swimlane
    And I syncronize "Test action" with "Test object"
    And I realize "Test action" "action" node
    And I submit the prompted "object" realization form
    When I save
    Then I should see a save success message