Feature: GE-Grid
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want to be able to configure grid options
  So that usability and layout is improved
  
  Scenario: Enabling Snapping

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
    And I toogle "snapping"
    Then "snapping" should be "enabled"
    When I toogle "snapping"
    Then "snapping" should be "disabled"
  
  Scenario: Enabling Grid

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
    And I toogle "grid"
    Then "grid" should be "enabled"
    When I toogle "grid"
    Then "grid" should be "disabled"