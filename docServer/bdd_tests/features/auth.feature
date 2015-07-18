Feature: Auth-Login
    # As a [Role]
    # I want [feature]
    # So that [Benefit]
  As a user
  I want a functional login feature
  So that the application can authenticate a user

  Scenario: Successful sign up

    When I sign up as "me", "1234", "me@me.com"
    Then log in for "me" should be successful


  Scenario: Failing sign up
	Given a set of specific users
     | username    	| first_name 			      | email						        | password |
     | me     		  | Ioannis Oikonomidis 	| s083928@student.dtu.dk 	| 1234 |
    When I sign up as "me", "1234", "me@me.com"
    Then I should see "This username is already taken. Please choose another."

  Scenario: Successful login

  	Given a set of specific users
     | username    	| first_name 		       	| email					         	| password |
     | me     		  | Ioannis Oikonomidis 	| s083928@student.dtu.dk 	| 1234 |
    When I log in as "me" "1234"
    Then log in for "me" should be successful

  Scenario: Failed login

  	Given a set of specific users
     | username    	| first_name 		     	  | email					        	| password |
     | me     		  | Ioannis Oikonomidis 	| s083928@student.dtu.dk 	| 1234 |
    When I log in as "me" "1235"
    Then I should see a login error message
