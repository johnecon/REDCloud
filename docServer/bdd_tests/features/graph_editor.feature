# Feature: Graph Editor
#     # As a [Role]
#     # I want [feature]
#     # So that [Benefit]
#   As a user
#   I want to be able to merge two object nodes of a graph and save
#   So that my work can be visualized in an activity diagram

#   Scenario: Graph Editor

#     Given I am a user
#     And I have created a project
#     And I log in
#     When I navigate to my projects
#     Then I should see my project

#     Given I assign me and a partner as contributors to my project
#     When I navigate to the graph editor of "my project"
#     Then I should see myDiagram

#     When I create an object node for me
#     And I create an object node for my partner
#     And  I merge these two object nodes
#     Then I should these nodes to a fork node linked to a new action node linked to one new object node

#     When I save
#     Then I should see a save success message
#     And There should be three object nodes, one action nodes, one control node and four edges in the database
