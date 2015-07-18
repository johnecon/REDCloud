Feature: GE-Editing
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to edit nodes
  So that I can configure the graph of a project

Scenario: Comment Edit

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
    And I change "Some feedback" "comment" node in "me" swimlane name to "Some Feedback 2"
    Then I should see "Some Feedback 2" "comment" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Swimlane Edit

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
    And I change the color of "me" swimlane to "#fffff"
    Then The color of "me" should be "#fffff"
    When I save
    Then I should see a save success message

Scenario: Future Object Edit

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
    And I change "Test object" "object" node in "me" swimlane name to "Test2 object"
    Then I should see "Test2 object" "object" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Future Action Edit

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
    And I create "Test action" "action" node in "me" swimlane
    And I change "Test action" "action" node in "me" swimlane name to "Test2 action"
    Then I should see "Test2 action" "action" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Present Object Edit

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
    And I realize "Test object" "object" node
    And I change "Realized Test object" "object" node in "me" swimlane name to "Test2 object"
    Then I should see "Test2 object" "object" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Present Action Edit

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
    And I create "Test action" "action" node in "me" swimlane
    And I realize "Test action" "action" node
    And I change "Realized Test action" "action" node in "me" swimlane name to "Test2 action"
    Then I should see "Test2 action" "action" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Past Object Edit

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
    And I archive "Test object" "object" node
    Then I should not be able to edit "Test object" "object" node in "me" swimlane
    When I save
    Then I should see a save success message

Scenario: Past Action Edit

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
    And I create "Test action" "action" node in "me" swimlane
    And I archive "Test action" "action" node
    Then I should not be able to edit "Test action" "action" node in "me" swimlane
    When I save
    Then I should see a save success message

