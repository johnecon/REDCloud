Feature: GE-Creation
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to create object and action nodes
  So that I can distribute tasks and allow collaboration of a team 
  
  Scenario: Comment Creation

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
    And I create "Some feedback" "comment" node in "me" swimlane
    Then I should see "Some feedback" "comment" node in "me" swimlane
    When I save
    Then I should see a save success message

  Scenario: Object Creation

  	Given a set of specific users
     | username    	| first_name 			    | email                   | password |
     | me           | Ioannis Oikonomidis | s083928@student.dtu.dk  | 1234 |
     | admin     		| admin 	            | admin@admin.dk 	        | admin |
     | my_partner   | John Econ           | johnnyecon@gmail.com		| 1234 |
    And a project "my project" created by "admin"
    And "me" contributes to "my project"
    And "my_partner" contributes to "my project"
    And "admin" exports "my project"`s graph
    When I log in as "me" "1234"
    And I navigate to the graph editor of "my project"
    And I create "Test object" "object" node in "me" swimlane
    Then I should see "Test object" "object" node in "me" swimlane
    When I save
    Then I should see a save success message

  Scenario: Action Creation

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
    Then I should see "Test action" "action" node in "me" swimlane
    When I save
    Then I should see a save success message