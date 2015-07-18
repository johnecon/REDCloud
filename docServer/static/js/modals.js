define(['bootbox.min', 'domReady!'], function(bootbox) {

    var getLoc = function(loc, y) {
        newLocArr = loc.split(" ");
        newLoc = newLocArr[0] + " " + (parseInt(newLocArr[1]) + y).toString();
        return newLoc;
    }

    var AUTOMATION_DELAY = 500;
    var deleteNode = function(event) {
        var node = getCurrentNode();
        bootbox.confirm("Are you sure you want to delete this node?", function(r) {
            if (r) {
                myDiagram.startTransaction("deleteNode");
                myDiagram.model.setDataProperty(myDiagram.selection.first().part.data, "delete", true);
                if (getCurrentNode().category != "Edge" && getCurrentNode().category != "Sync") {
                    myDiagram.selection.first().linksConnected.each(function(b) {
                        myDiagram.model.setDataProperty(b.part.data, "delete", true);
                    });
                }
                myDiagram.commitTransaction("deleteNode");
            }
        }).on('hide.bs.modal', function (e) {
            myDiagram.toolManager.contextMenuTool.stopTool();
        })
    };

    var synchronize = function() {
        bootbox.confirm("Are you sure you want to synchronize these nodes?", function(r) {
            if (r) {
                myDiagram.startTransaction("synchronize");
                var selectedOrderedNodes = _.chain(myDiagram.selection.toArray()).
                sortBy(function(n) { return n.location.x; }).
                value();
                _.reduce(selectedOrderedNodes, function(nodeOne, nodeTwo) {
                    var syncEdge = {category: "Sync", from: nodeOne.part.data.key, to: nodeTwo.part.data.key};
                    myDiagram.model.addLinkData(syncEdge);
                    return nodeTwo;
                }) ;
                myDiagram.commitTransaction("synchronize");
                objectRealizationManager.reset();
            }
        }).on('hide.bs.modal', function (e) {
            myDiagram.toolManager.contextMenuTool.stopTool();
        })
    }

    var undoDeleteNode = function(event) {
        var node = getCurrentNode();
        myDiagram.startTransaction("undoDeleteNode");
        myDiagram.model.setDataProperty(myDiagram.selection.first().part.data, "delete", false);
        myDiagram.commitTransaction("undoDeleteNode");
        myDiagram.toolManager.contextMenuTool.stopTool();
    };

    function getCurrentNode() {
        return myDiagram.selection.first().part.data;
    };

    var objectRealizationManager = {
            reset: function() {
                this.robot = new Robot(myDiagram);
                this.objects = [];
                this.synced = {};
                var that = this;
                myDiagram.links.each(function(n) {
                    if (n.category == "Sync" && !n.part.data.delete) {
                        var from = n.part.data.from;
                        var to = n.part.data.to;
                        var fromNode = myDiagram.findNodeForKey(n.part.data.from);
                        var toNode = myDiagram.findNodeForKey(n.part.data.to);
                        that.synced[from] = that.synced[from] == undefined ? [] : that.synced[from];
                        that.synced[to] = that.synced[to] == undefined ? [] : that.synced[to];
                        if (toNode.part.data.tense == FUTURE_TENSE) {
                        }
                            that.synced[from].push(toNode);
                        if (fromNode.part.data.tense == FUTURE_TENSE) {
                        }
                            that.synced[to].push(fromNode);
                    } else if (n.part.data && !n.part.data.delete) {
                        var from = n.part.data.from;
                        var fromNode = myDiagram.findNodeForKey(from);
                        var to = n.part.data.to;
                        var toNode = myDiagram.findNodeForKey(to);
                        if (fromNode.part.data.category.startsWith(ACTION_CATEGORY_PREFIX) &&
                            toNode.part.data.category == "Object") {
                            that.synced[from] = that.synced[from] == undefined ? [] : that.synced[from];
                            that.synced[from].push(toNode);
                        }
                    }
                });
            },
            object: null,
            objects: [],
            objectsAlreadyShown: [],
            robot: null,
            synced: null,
            next: function() {
                this.object = this.objects.pop();
                return this.object;
            },
            current: function() {
                return this.object;
            },
            updateObjects: function(key) {
                var that = this;
                _(this.synced[key]).each(function(n) {
                    if (that.objectsAlreadyShown.indexOf(n) == -1) {
                        that.objects.push(n);  
                    }
                });
            },
            run: function() {
                this.next();
                var node = this.current();
                if (this.objects.length >= 0) {
                    if (node && node.part.data.tense == FUTURE_TENSE && node.part.data.category == "Object") {
                        this.robot.mouseDown(node.location.x, node.location.y, 0, {right: true});
                        this.robot.mouseUp(node.location.x, node.location.y, 1, {right: true});
                        setTimeout(function() {$("#realizeObject").click();}, AUTOMATION_DELAY);
                    } else if (node && node.part.data.tense == FUTURE_TENSE && node.part.data.category.startsWith(ACTION_CATEGORY_PREFIX)) {
                        this.robot.mouseDown(node.location.x, node.location.y, 0, {right: true});
                        this.robot.mouseUp(node.location.x, node.location.y, 1, {right: true});
                        setTimeout(function() {$("#realizeAction").click();}, AUTOMATION_DELAY);
                    } else if (node && (node.part.data.category.startsWith(ACTION_CATEGORY_PREFIX) || node.part.data.category == "Object")) {
                        this.objectsAlreadyShown.push(node);
                        this.updateObjects(node.part.data.key);
                        this.run();
                    } else {
                        this.reset();
                    }
                }
            }
        };

    require(['jquery.fileDownload', 'colorpicker'], function() {
        var usersLength = users.length;
        var resources = [];
        var updateNode = function(node, properties) {
            for (property in properties) {
                myDiagram.model.setDataProperty(node, property, properties[property]);
            }
            myDiagram.model.setDataProperty(node, "is_modified", true);
        };

        function rainbow(numOfSteps, step) {
            // This function generates vibrant, "evenly spaced" colours (i.e. no clustering). This is ideal for creating easily distinguishable vibrant markers in Google Maps and other apps.
            // Adam Cole, 2011-Sept-14
            // HSV to RBG adapted from: http://mjijackson.com/2008/02/rgb-to-hsl-and-rgb-to-hsv-color-model-conversion-algorithms-in-javascript
            var r, g, b;
            var h = step / numOfSteps;
            var i = ~~(h * 6);
            var f = h * 6 - i;
            var q = 1 - f;
            switch(i % 6){
                case 0: r = 1, g = f, b = 0; break;
                case 1: r = q, g = 1, b = 0; break;
                case 2: r = 0, g = 1, b = f; break;
                case 3: r = 0, g = q, b = 1; break;
                case 4: r = f, g = 0, b = 1; break;
                case 5: r = 1, g = 0, b = q; break;
            }
            var c = "#" + ("00" + (~ ~(r * 255)).toString(16)).slice(-2) + ("00" + (~ ~(g * 255)).toString(16)).slice(-2) + ("00" + (~ ~(b * 255)).toString(16)).slice(-2);
            return (c);
        }

        function getCurrentUsers() {
            var curUsers = [];
            var it = myDiagram.nodes;
            while (it.next()) {
                if (it.key.category == "SwimLane") {
                    curUsers.push(it.key.part.data.key);
                }

            }
            return curUsers;
        }

        var i = 0;
        function getColor() {
            i++;
            return rainbow(usersLength, i);
        }

        function getDate() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1; //January is 0!

            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd
            }
            if (mm < 10) {
                mm = '0' + mm
            }
            return yyyy + '-' + mm + '-' + dd;
        }

        function hideModal(element) {
            myDiagram.toolManager.contextMenuTool.stopTool();
            element.hide().appendTo('body');
        }

        function showModal(element) {
            element.show().validate().resetForm();
            element.find('.form-group').each(function() {
                jQuery(this).removeClass('has-error').removeClass('has-success');
            })
        }

        function highlight (element) {
            $(element).closest('.form-group')
            .removeClass('has-success').addClass('has-error');
        }

        function success (element) {
            element.addClass('valid').closest('.form-group')
            .removeClass('has-error').addClass('has-success');
            element.closest('.control-label').remove();
        }

        function calculateChangeMessage(model) {
            function appendToString(s, append) {
                return s != "" ? s + ", " + append : append;
            }
            var node = getCurrentNode();
            var change = "";
            if (node.name != model.name) {
                change = appendToString(change, "Renaming");
            }
            if (node.public != model.public) {
                if (model.public == "YES") {
                    change = appendToString(change, model.public == "TRUE" ? "Changing to Secret" : "Changing to Public");
                }
            }
            if (node.resourcePk != model.resourcePk) {
                change = appendToString(change, "Resource Update")
            }
            return change;
        }

        function createObjectNode(modal) {
            myDiagram.startTransaction("createObjectNode");
            var model = {
                name: modal.find('[name="name"]').val(),
                description: modal.find('[name="description"]').val(),
                tense: modal.find('[name="tense"]').val(),
                public: modal.find('[name="public"]').prop('checked') ? "YES" : "NO",
                start: modal.find('[name="start"]').prop('checked') ? "YES" : "NO"
            };
            var node = getCurrentNode();
            var path,resourcePk;
            _(jQuery(modal).find('[name^="resource"]')).each(function(input) {
                path = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[0];
                resourcePk = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[1];
            });
            var offset = model.start != "YES" ? 0 : 200;
            var objectNode = {
                key: getKey(),
                name: model.name,
                description: model.description,
                category: "Object",
                public: model.public,
                tense: resourcePk == null ? FUTURE_TENSE : model.tense,
                strokeDashArray: model.tense == FUTURE_TENSE || resourcePk == null ? [5, 10] : null,
                fill: resourcePk != null && model.tense == PAST_TENSE ? GREY_BLUE : (model.tense == PRESENT_TENSE ? "lightblue" : "white"),
                resourcePk: resourcePk,
                resourceName: path,
                group: node.key,
                createdBy: current_user.username,
                loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (offset + myDiagram.toolManager.contextMenuTool.mouseDownPoint.y).toString(),
                date: getDate()
            };
            if (model.start == "YES")
            {
                var startNode = {
                    key: getKey(),
                    category: "Start",
                    group: node.key,
                    createdBy: current_user.username,
                    loc: getLoc(objectNode.loc, -200),
                    date: getDate()
                };
                var actionNode = {
                        key: getKey(),
                        tense: FUTURE_TENSE,
                        category: "Action-In",
                        name: "Creating " + model.name,
                        description: "",
                        operation_type: OPERATION_TYPE_INTERNAL,
                        group: node.key,
                        fill: "white",
                        strokeDashArray: [5, 10],
                        createdBy: current_user.username,
                        loc: getLoc(objectNode.loc, -100),
                        date: getDate()
                    };
                var startActionEdge = {category: "Edge", from: startNode.key, to: actionNode.key};
                var actionObjectEdge = {category: "Edge", from: actionNode.key, to: objectNode.key};
                myDiagram.model.addNodeData(actionNode);
                myDiagram.model.addNodeData(startNode);
                myDiagram.model.addNodeData(objectNode);
                myDiagram.model.addLinkData(startActionEdge);
                myDiagram.model.addLinkData(actionObjectEdge);
            } else {
                myDiagram.model.addNodeData(objectNode);
            }


            myDiagram.commitTransaction("createObjectNode");
        }

        var templates;
        var diff;
        var keyMappings = {};

        function importTemplate(modal) {
            myDiagramGroupKeys = [];
            myDiagram.nodes.each(function(n) {
                if (n.part.data.category == "SwimLane") {
                   myDiagramGroupKeys.push(n.part.data.key);
                }
            });
            _(templates).each(function(template) {
                if (template.pk == modal.find('option:selected').val()) {
                    myDiagram.startTransaction("importTemplate");
                    myTemplateGroupKeys = [];
                    _(template.graph_elements).each(function(element){
                    element.pk = null;
                        if (["SwimLane"].indexOf(element.category) > -1) {
                           myTemplateGroupKeys.push(element.key);
                        }
                    });
                    diff = Math.abs(myTemplateGroupKeys.length - myDiagramGroupKeys.length);
                    if (myDiagramGroupKeys.length < myTemplateGroupKeys.length) {
                        for (i=0;i<diff;i++) {
                            myDiagramGroupKeys.push(myDiagramGroupKeys[myDiagramGroupKeys.length-1]);
                        }
                    } else if (myTemplateGroupKeys.length < myDiagramGroupKeys.length) {
                        for (i=0;i<diff;i++) {
                            myTemplateGroupKeys.push(myTemplateGroupKeys[myTemplateGroupKeys.length-1]);
                        }
                    }
                    for(var i = 0; i < myTemplateGroupKeys.length; i += 1) {
                        keyMappings[ myTemplateGroupKeys[i] ] = myDiagramGroupKeys[i];
                    }
                    _(template.graph_elements).each(function(element){
                        element.pk = null;
                        element.group = keyMappings[element.group];
                        if (["Pool", "SwimLane", "Sync", "Edge"].indexOf(element.category) == -1) {
                            myDiagram.model.addNodeData(element);
                        }
                    });
                    _(template.graph_elements).each(function(element){
                        if (["Sync", "Edge"].indexOf(element.category) > -1) {
                            element.from = element.src;
                            element.to = element.tgt;
                            delete element.tgt;
                            delete element.src;
                            myDiagram.model.addLinkData(element);
                        }
                    });
                    myDiagram.layout.invalidateLayout();
                    myDiagram.findTopLevelGroups().each(function(g) { if (g.category === "Pool") g.layout.invalidateLayout(); });
                    myDiagram.layoutDiagram();
                    myDiagram.commitTransaction("importTemplate");
                }
            });
        }

        function importObject(modal) {
            myDiagram.startTransaction("importObject");
            var model = {
                resource: modal.find('[name="resource"]').val(),
                display: modal.find('option:selected').text(),
                name: modal.find('[name="name"]').val()
            };
            var node = getCurrentNode();
            // var boundary = myDiagram.findNodeForKey("Boundary");
            // var defaultPort = boundary.findPort("");

            // while (boundary.findPort("be" + i.toString()) !== defaultPort) i++;           // now this new port name is unique within the whole Node because of the side prefix
            // var name = "be" + i.toString();
            // // get the Array of port data to be modified
            // var arr = boundary.data["boundaryEventArray"];
            // if (arr) {
            //     // create a new port data object
            //     var newportdata = {
            //         portId: name,
            //         eventType: 2,
            //         color: "white",
            //         alignmentIndex: i
            //     // if you add port data properties here, you should copy them in copyPortData above
            //     };
            //     // and add it to the Array of port data
            //     myDiagram.model.insertArrayItem(arr, -1, newportdata);
            // }
            var resource = _(resources).filter(function(r) {return r.pk==model.resource;})[0];
            var fileName = "";
            var modelName = "";
            var actionNode = {
                    key: getKey(),
                    category: ACTION_CATEGORY_PREFIX + OPERATION_TYPE_IMPORT,
                    tense: FUTURE_TENSE,
                    operation_type: OPERATION_TYPE_IMPORT,
                    strokeDashArray: [5, 10],
                    fill: 'white',
                    name: "Importing " + model.display,
                    description: "",
                    group: node.key,
                    createdBy: current_user.username,
                    date: getDate(),
                    loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (myDiagram.toolManager.contextMenuTool.mouseDownPoint.y).toString()
                };
            myDiagram.model.addNodeData(actionNode);
            if (resource && resource.type == "Folder") {
                var counter = -50;
                _(_(resources).filter(function(r) {return r.pk==model.resource;})[0].items).each(
                    function(file) {
                        fileName = file.name.split("_")[0];
                        modelName = model.name != "" ? model.name + "-" : "";
                        var objectNode = {
                            key: getKey(),
                            name: modelName + fileName,
                            category: "Object",
                            public: "NO",
                            tense: FUTURE_TENSE,
                            strokeDashArray: [5, 10],
                            fill: 'white',
                            resourcePk: file ? file.pk : null,
                            resourceName: file ? fileName : null,
                            group: node.key,
                            createdBy: current_user.username,
                            loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x + counter).toString() + " " + (myDiagram.toolManager.contextMenuTool.mouseDownPoint.y + 100).toString(),
                            date: getDate(),
                        };
                        counter += 100;
                        var actionToObjectEdge = {category: "Edge", from: actionNode.key, to: objectNode.key};
                        myDiagram.model.addNodeData(objectNode);
                        myDiagram.model.addLinkData(actionToObjectEdge);
                    });
            } else {
                fileName = resource ? resource.name.split("_")[0] : '';
                modelName = fileName ? model.name + "-" + fileName : model.name;
                var objectNode = {
                    key: getKey(),
                    name: modelName,
                    category: "Object",
                    public: "NO",
                    strokeDashArray: [5, 10],
                    fill: 'white',
                    tense: FUTURE_TENSE,
                    resourcePk: resource ? resource.pk : null,
                    resourceName: fileName == '' ? null : fileName,
                    group: node.key,
                    createdBy: current_user.username,
                    loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (myDiagram.toolManager.contextMenuTool.mouseDownPoint.y + 100).toString(),
                    date: getDate(),
                };
                var actionToObjectEdge = {category: "Edge", from: actionNode.key, to: objectNode.key};
                myDiagram.model.addNodeData(objectNode);
                myDiagram.model.addLinkData(actionToObjectEdge);
            }
            myDiagram.commitTransaction("importObject");
        }

        function editObjectNode(modal) {
            myDiagram.startTransaction("editObjectNode");
            var change;
            var description;
            var node = getCurrentNode();
            var model = {
                change: modal.find('[name="change"]').val(),
                description: modal.find('[name="description"]').val(),
                name: modal.find('[name="name"]').val(),
                tense: modal.find('[name="tense"]').val(),
                public: modal.find('[name="public"]').prop('checked') ? "YES" : "NO"
            };
            model.resourcePk = node.resourcePk == "" ? null : node.resourcePk;
            model.resourceName = node.resourceName  == "" ? null : node.resourceName;
            _(jQuery(modal).find('[name^="resource"]')).each(function(input) {
                model.resourcePk = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[0];
                model.resourceName = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[1];
            });
            myDiagram.model.setDataProperty(node, 'fill', 'white');
            if (model.tense == PRESENT_TENSE && node.tense == FUTURE_TENSE) { //realize
                myDiagram.model.setDataProperty(node, 'realized_by', current_user.username);
                myDiagram.model.setDataProperty(node, 'toLinkable', false);
                myDiagram.model.setDataProperty(node, 'date_realized', getDate());
            }
            if (model.tense == FUTURE_TENSE ||
                model.resourcePk != null) {
                myDiagram.model.setDataProperty(node, 'tense', model.tense);
                myDiagram.model.setDataProperty(node, 'strokeDashArray', model.tense == FUTURE_TENSE ? [5, 10] : null);
                myDiagram.model.setDataProperty(node, 'fill', model.tense == PRESENT_TENSE ? 'lightblue' : 'white');
                if (model.tense == PAST_TENSE) {
                    myDiagram.model.setDataProperty(node, 'fill', GREY_BLUE);
                }
            }
            myDiagram.model.setDataProperty(node, 'name', model.name);
            myDiagram.model.setDataProperty(node, 'description', model.description);
            myDiagram.model.setDataProperty(node, 'resourcePk', model.resourcePk);
            myDiagram.model.setDataProperty(node, 'resourceName', model.resourceName);
            myDiagram.model.setDataProperty(node, 'public', model.public);
            myDiagram.commitTransaction("editObjectNode");
        }

        function extendObjectNode(modal) {
            myDiagram.startTransaction("extendObjectNode");
            var change;
            var description;
            var node = getCurrentNode();
            var model = {
                change: modal.find('[name="change"]').val(),
                description: modal.find('[name="description"]').val(),
                name: modal.find('[name="name"]').val(),
                public: modal.find('[name="public"]').prop('checked') ? "YES" : "NO"
            };
            model.resourcePk = node.resourcePk;
            model.resourceName = node.resourceName;
            _(jQuery(modal).find('[name^="resource"]')).each(function(input) {
                model.resourcePk = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[0];
                model.resourceName = input.value.split(RESOURCE_PK_NAME_SEPARATOR)[1];
            });
            if (model.change) {
                change = model.change;
                changeDescription = model.changeDescription;
            } else {
                change = calculateChangeMessage(model);
                changeDescription = "";
            }
            if (node.resourcePk) {
                var actionNode = {
                    key: getKey(),
                    category: "Action",
                    name: change,
                    description: changeDescription,
                    group: node.group,
                    createdBy: current_user.username,
                    date: getDate(),
                    loc: getLoc(node.loc, 100)
                };
                var objectNode = {
                    key: getKey(),
                    name: model.name,
                    description: model.description,
                    category: "Object",
                    public: model.public,
                    resourcePk: model.resourcePk,
                    resourceName: model.resourceName,
                    group: node.group,
                    createdBy: current_user.username,
                    date: getDate(),
                    loc: getLoc(node.loc, 200)
                };
                var oldObjectNewActionEdge = {category: "Edge", from: node.key, to: actionNode.key};
                var newActionToNewObjectEdge = {category: "Edge", from: actionNode.key, to: objectNode.key};
                myDiagram.model.addNodeData(actionNode);
                myDiagram.model.addNodeData(objectNode);
                myDiagram.model.addLinkData(oldObjectNewActionEdge);
                myDiagram.model.addLinkData(newActionToNewObjectEdge);
            } else {
                myDiagram.model.setDataProperty(node, 'name', model.name);
                myDiagram.model.setDataProperty(node, 'resourcePk', model.resourcePk);
                myDiagram.model.setDataProperty(node, 'resourceName', model.resourceName);
                myDiagram.model.setDataProperty(node, 'public', model.public);
            }
            myDiagram.commitTransaction("extendObjectNode");
        }

        function editActionNode(modal) {
            myDiagram.startTransaction("editActionNode");
            var node = getCurrentNode();
            var name = modal.find('[name="name"]').val();
            var description = modal.find('[name="description"]').val();
            var tense = modal.find('[name="tense"]').val();
            var operation_type = modal.find('[name="operation_type"]').val();
            var realized_by=null;
            var date_realized=null;
            if (node.category == "SwimLane") {
                if (tense == PRESENT_TENSE) {
                    realized_by = current_user.username;
                    date_realized = getDate();
                }
                var actionNode = {
                    key: getKey(),
                    category: ACTION_CATEGORY_PREFIX + operation_type,
                    tense: tense,
                    operation_type: operation_type,
                    name: name,
                    description: description,
                    strokeDashArray: tense == FUTURE_TENSE ? [5, 10] : null,
                    fill: tense == PRESENT_TENSE ? 'lightyellow' : 'white',
                    group: node.key,
                    createdBy: current_user.username,
                    date: getDate(),
                    loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (myDiagram.toolManager.contextMenuTool.mouseDownPoint.y).toString()
                };
                myDiagram.model.addNodeData(actionNode);
            } else {
                myDiagram.model.setDataProperty(node, 'fill', 'white');
                if (tense == PAST_TENSE) {
                    myDiagram.model.setDataProperty(node, 'fill', GREY_YELLOW);
                }else if (tense == PRESENT_TENSE) {
                    myDiagram.model.setDataProperty(node, 'fill', 'lightyellow');
                    myDiagram.model.setDataProperty(node, 'toLinkable', false);
                    if (node.tense == FUTURE_TENSE) {
                        myDiagram.model.setDataProperty(node, 'realized_by', current_user.username);
                        myDiagram.model.setDataProperty(node, 'date_realized', getDate());
                    }
                }
                myDiagram.model.setCategoryForNodeData(node, ACTION_CATEGORY_PREFIX + operation_type);
                myDiagram.model.setDataProperty(node, 'name', modal.find('[name="name"]').val());
                myDiagram.model.setDataProperty(node, 'description', modal.find('[name="description"]').val());
                myDiagram.model.setDataProperty(node, 'tense', tense);
                myDiagram.model.setDataProperty(node, 'operation_type', operation_type);
                myDiagram.model.setDataProperty(node, 'strokeDashArray', tense == FUTURE_TENSE ? [5, 10] : null);
            }
            myDiagram.commitTransaction("editActionNode");
        }

        function editSwimLane() {
            myDiagram.startTransaction("editSwimLane");
            var node = getCurrentNode();
            myDiagram.model.setDataProperty(node, 'color', jQuery('#editSwimLaneModal').find('[name="color"]').val());
            myDiagram.commitTransaction("editSwimLane");
        }

        function editComment(modal) {
            myDiagram.startTransaction("editComment");
            var node = getCurrentNode();
            myDiagram.model.setDataProperty(node, 'name', modal.find('[name="name"]').val());
            myDiagram.commitTransaction("editComment");
        }

        function comment(modal) {

            myDiagram.startTransaction("comment");
            var node = getCurrentNode();
            var model = {
                name: modal.find('[name="name"]').val()
            }
            var commentNode = {
                key: getKey(),
                category: "Comment",
                name: model.name,
                group: node.key,
                createdBy: current_user.username,
                loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (myDiagram.toolManager.contextMenuTool.mouseDownPoint.y).toString(),
                date: getDate()
            };
            myDiagram.model.addNodeData(commentNode);
            myDiagram.commitTransaction("comment");
        }

        function addSwimLane(user) {

            myDiagram.startTransaction("addSwimLane");
            users = _.filter(users, function (u) {
                return u.name != user;
            });
            var lane = {
                key: user,
                isGroup: true,
                // group:"Boundary",
                category: "SwimLane",
                color: getColor(),
                date: getDate(),
                createdBy: current_user.username
            };
            myDiagram.model.addNodeData(lane);
            myDiagram.commitTransaction("addSwimLane");
        }

        function exportObjects(modal) {
            myDiagram.startTransaction("exportObjects");
            var model = {
                name: modal.find('[name="name"]').val(),
                description: modal.find('[name="description"]').val()
            };
            var resourcePks = [];
            var selectedObjects = "";
            var counter = 0;
            var froms = [];
            myDiagram.selection.each(function(node) {
                if (counter == myDiagram.selection.count - 1) {
                    selectedObjects = selectedObjects.substring(0, selectedObjects.length - 2);
                    if (myDiagram.selection.count > 1) {
                        selectedObjects += " and ";
                    }
                }
                froms.push(node.part.data.key);
                resourcePks.push(node.part.data.resourcePk);
                selectedObjects += node.part.data.name;
                if (counter < myDiagram.selection.count - 1) {
                    selectedObjects += ", ";
                }
                counter++;
            });
            var southestNode = myDiagram.selection.first();
            myDiagram.selection.each(function(node) {
                if (node.part.data.loc.split(" ")[1] > southestNode.part.data.loc.split(" ")[1]) {
                    southestNode = node;
                }
            });
            jQuery.ajax({
                type: "POST",
                url: "resources/export",
                contentType: "application/json",
                data: JSON.stringify({name: model.name, pks: resourcePks}),
                success: function (response) {
                    var objectNode = {
                        key: getKey(),
                        name: model.name,
                        category: "Object",
                        public: "YES",
                        tense: FUTURE_TENSE,
                        resourceName: response.resourceName,
                        resourcePk: response.resourcePk,
                        group: southestNode.part.data.group,
                        createdBy: current_user.username,
                        date: getDate(),
                        strokeDashArray: [5, 10],
                        loc: getLoc(southestNode.part.data.loc, 200 + Math.random()*10)
                    };
                    var actionNode = {
                        key: getKey(),
                        category: ACTION_CATEGORY_PREFIX + OPERATION_TYPE_EXPORT,
                        tense: FUTURE_TENSE,
                        operation_type: OPERATION_TYPE_EXPORT,
                        name: "Exporting " + selectedObjects + " into " + model.name,
                        description: model.description,
                        group: southestNode.part.data.group,
                        createdBy: current_user.username,
                        strokeDashArray: [5, 10],
                        date: getDate(),
                        loc: getLoc(southestNode.part.data.loc, 100 + Math.random()*10)
                    };
                    for(var i=0;i<froms.length;i++) {
                        myDiagram.model.addLinkData({category: "Edge", from: froms[i], to: actionNode.key});
                    }
                    myDiagram.model.addNodeData(actionNode);
                    selectedObjects = selectedObjects.substring(0, selectedObjects.length - 2);
                    var actionObjectEdge = {category: "Edge", from: actionNode.key, to: objectNode.key};
                    myDiagram.model.addNodeData(objectNode);
                    myDiagram.model.addNodeData(actionNode);
                    myDiagram.model.addLinkData(actionObjectEdge);
                    myDiagram.commitTransaction("exportObjects");
                },
                error: function (response) {
                    console.log(response);
                },
                dataType: "json"
            });
        }

        var editActionInput = jQuery('#action-name-input');
        var editActionModal = jQuery('#editActionModal');
        editActionModal.validate({
            rules: {
                name: {
                    required: true,
                    minlength: 2
                }
            },
            errorClass: "control-label",
            highlight: function (element) {
                $(element).closest('.form-group')
                .removeClass('has-success').addClass('has-error');
            },
            success: function (element) {
                element.addClass('valid').closest('.form-group')
                .removeClass('has-error').addClass('has-success');
                element.closest('.control-label').remove();
            },
            messages: {
                name: {
                    required: "Please enter a change title",
                    minlength: "A change title must consist of at least 2 characters"
                }
            },
            submitHandler: function (form) {
                editActionNode(editActionModal);
                bootbox.hideAll();
            }
        });
        var editActionSelectTense = editActionModal
                .find('[name="tense"]');
        jQuery('#editAction').on('click', function () {
            var node = getCurrentNode();
            editActionSelectTense.find('option').remove().end();
            if (node.tense == FUTURE_TENSE) {
                editActionSelectTense.append($('<option>', {
                        value: FUTURE_TENSE,
                        text : "Future"
                    }));
            }
            else if (node.tense == PRESENT_TENSE) {
                editActionSelectTense.append($('<option>', {
                        value: PRESENT_TENSE,
                        text : "Present"
                    }));
            }
            else if (node.tense == PAST_TENSE) {
                editActionSelectTense.append($('<option>', {
                        value: PAST_TENSE,
                        text : "Past"
                    }));
            } else {
                editActionSelectTense.append($('<option>', {
                        value: FUTURE_TENSE,
                        text : "Future"
                    }));
            }
            editActionModal
                .find('[name="name"]').val(node.name).prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="description"]').val(node.description).prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="operation_type"]').val(node.operation_type).prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="tense"]').val(node.tense).prop('disabled', true).end();

            bootbox
                .dialog({
                    title: 'Edit Action Node',
                    message: editActionModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(editActionModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(editActionModal);
                })
                .modal('show');
            editActionInput.focus();
        });
        jQuery('#createAction').on('click', function () {
            var node = getCurrentNode();
            editActionSelectTense.find('option').remove().end();
            editActionSelectTense.append($('<option>', {
                    value: FUTURE_TENSE,
                    text : "Future"
                }));
            editActionModal
                .find('[name="name"]').val("").prop('disabled', false).end()
                .find('[name="description"]').val("").prop('disabled', false).end()
                .find('[name="operation_type"]').val(OPERATION_TYPE_INTERNAL).prop('disabled', false).end()
                .find('[name="tense"]').val(FUTURE_TENSE).prop('disabled', true).end();

            bootbox
                .dialog({
                    title: 'Create Action Node',
                    message: editActionModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(editActionModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(editActionModal);
                })
                .modal('show');
            editActionInput.focus();
        });

        var realizeActionInput = jQuery('#realize-action-name-input');
        var realizeActionModal = jQuery('#realizeActionModal');
        realizeActionModal.validate({
            rules: {
                name: {
                    required: true,
                    minlength: 2
                }
            },
            errorClass: "control-label",
            highlight: function (element) {
                $(element).closest('.form-group')
                .removeClass('has-success').addClass('has-error');
            },
            success: function (element) {
                element.addClass('valid').closest('.form-group')
                .removeClass('has-error').addClass('has-success');
                element.closest('.control-label').remove();
            },
            messages: {
                name: {
                    required: "Please enter a change title",
                    minlength: "A change title must consist of at least 2 characters"
                }
            },
            submitHandler: function (form) {
                editActionNode(realizeActionModal);
                bootbox.hideAll();
                // myDiagram.selection.first().linksConnected.each(function(b) {
                //     if (!b.part.data.delete && b.part.data.to != getCurrentNode().key) {
                //         objectRealizationManager.objects.push(myDiagram.findNodeForKey(b.part.data.to));
                //     }
                // });
                objectRealizationManager.updateObjects(getCurrentNode().key);
                objectRealizationManager.objectsAlreadyShown.push(myDiagram.findNodeForKey(getCurrentNode().key));
                objectRealizationManager.run();
            }
        });
        jQuery('#realizeAction').on('click', function () {
            var node = getCurrentNode();
            realizeActionModal
                .find('[name="name"]').val(node.name).prop('disabled', false).end()
                .find('[name="description"]').val(node.description).end()
                .find('[name="tense"]').val(PRESENT_TENSE).prop('disabled', true).end()
                .find('[name="operation_type"]').val(node.operation_type).prop('disabled', true).end();

            bootbox
                .dialog({
                    title: 'Realize Action Node',
                    message: realizeActionModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        objectRealizationManager.reset();
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(realizeActionModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(realizeActionModal);
                })
                .modal('show');
            realizeActionInput.focus();
        });

        var editSwimLaneModal = jQuery('#editSwimLaneModal');
        var selectColor = editSwimLaneModal
                .find('[name="color"]');
        editSwimLaneModal.validate({
            rules: {
                color: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                color: {
                    required: "Please pick a color"
                }
            },
            submitHandler: function (form) {
                editSwimLane(selectColor.val());
                bootbox.hideAll();
            }
        });
        jQuery('#editSwimLane').on('click', function () {
            var node = getCurrentNode();
            selectColor.val(node.color).end();
            editSwimLaneModal.find('[name="name"]').val(node.name);
            bootbox
                .dialog({
                    title: 'Edit User',
                    message: editSwimLaneModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        selectColor.ColorPickerHide();
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(editSwimLaneModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(editSwimLaneModal);
                })
                .modal('show');
            // selectColor.click();
        });

        var editObjectModal = jQuery('#editObjectModal');
        var editObjectSelectTense = editObjectModal
                .find('[name="tense"]');
        var editObjectInput = jQuery('#edit-object-name-input');
        editObjectModal.validate({
            rules: {
                name: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                name: {
                    required: "Please enter a name"
                }
            },
            submitHandler: function (form) {
                editObjectNode(editObjectModal);
                bootbox.hideAll();
            }
        });
        jQuery('#editObject').on('click', function () {
            var node = getCurrentNode();
            editObjectSelectTense.find('option').remove().end();
            if (node.tense == FUTURE_TENSE) {
                editObjectSelectTense.append($('<option>', {
                        value: FUTURE_TENSE,
                        text : "Future"
                    }));
            }
            else if (node.tense == PRESENT_TENSE) {
                editObjectSelectTense.append($('<option>', {
                        value: PRESENT_TENSE,
                        text : "Present"
                    }));
            }
            else if (node.tense == PAST_TENSE) {
                editObjectSelectTense.append($('<option>', {
                        value: PAST_TENSE,
                        text : "Past"
                    }));
            } else {
                editObjectSelectTense.append($('<option>', {
                        value: FUTURE_TENSE,
                        text : "Future"
                    }));
            }
            var resource = (node.resourceName != undefined) ? "<a>" + node.resourceName + "</a>" : "";
            loadUploader(editObjectModal.find('.file-uploader')[0]);
            editObjectModal
                .find('[name="name"]').val(node.name).prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="description"]').val(node.description).prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="tense"]').val(node.tense).prop('disabled', true).end()
                .find('[class="file-name"]').html(resource).end()
                .find('[name="file"]').prop('disabled', node.tense == PAST_TENSE).end()
                .find('[name="public"]').prop("checked", node.public == "YES").prop('disabled', node.tense == PAST_TENSE).end();
            insertFileInput(editObjectModal.find('[class="file-input"]'),
                "resource", node.resourcePk != undefined ? node.resourcePk + RESOURCE_PK_NAME_SEPARATOR + node.resourceName : "");
            bootbox
                .dialog({
                    title: 'Edit Artifact',
                    message: editObjectModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(editObjectModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(editObjectModal);
                })
                .modal('show');
            editObjectInput.focus();
        });

        var commentInput = jQuery('#comment-name-input');
        var commentModal = jQuery('#commentModal');
        commentModal.validate({
            rules: {
                name: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                name: {
                    required: "Please enter a name"
                }
            },
            submitHandler: function (form) {
                comment(commentModal);
                bootbox.hideAll();
            }
        });
        jQuery('#comment').on('click', function () {
            var node = getCurrentNode();
            commentModal
                .find('[name="name"]').val("").end()

            bootbox
                .dialog({
                    title: 'Add Comment',
                    message: commentModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(commentModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(commentModal);
                })
                .modal('show');
            commentInput.focus();
        });

        var editCommentInput = jQuery('#edit-comment-name-input');
        var editCommentModal = jQuery('#editCommentModal');
        editCommentModal.validate({
            rules: {
                name: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                name: {
                    required: "Please enter a name"
                }
            },
            submitHandler: function (form) {
                editComment(editCommentModal);
                bootbox.hideAll();
            }
        });
        jQuery('#editComment').on('click', function () {
            var node = getCurrentNode();
            editCommentModal
                .find('[name="name"]').val("").end()

            bootbox
                .dialog({
                    title: 'Edit Comment',
                    message: editCommentModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(editCommentModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(editCommentModal);
                })
                .modal('show');
            editCommentInput.focus();
        });

        var importObjectInput = jQuery("#import-object-name-input");
        var importObjectModal = jQuery('#importObjectModal');
        var selectResource = importObjectModal
                .find('[name="resource"]');
        importObjectModal.validate({
            rules: {
                name: {
                    required: true
                },
                resource: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                resource: {
                    required: "Please pick a file"
                },
                name: {
                    required: "Please enter a name"
                }
            },
            submitHandler: function (form) {
                importObject(importObjectModal);
                bootbox.hideAll();
            }
        });
        jQuery('#importObject').on('click', function () {
            selectResource.find('option').remove().end().append('<option value="">-- Pick a Resource --</option>').val('');
            jQuery.ajax({
                type: "GET",
                url: "/resources",
                contentType: "application/json",
                success: function (response) {
                    resources = response.data;
                    $.each(resources, function (i, resource) {
                        selectResource.append($('<option>', {
                            value: resource.pk,
                            text: resource.name
                        }));
                    });
                },
                error: function(r) {
                    console.log(r);
                }
            });
            importObjectModal
                .find('[name="name"]').val('').end()

            bootbox
                .dialog({
                    title: 'Import Artifact',
                    message: importObjectModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(importObjectModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(importObjectModal);
                })
                .modal('show');
            importObjectInput.focus();
        });

        var importTemplateModal = jQuery('#importTemplateModal');
        var selectTemplate = importTemplateModal
                .find('[name="template"]');
        importTemplateModal.validate({
            rules: {
                template: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                template: {
                    required: "Please pick a template"
                }
            },
            submitHandler: function (form) {
                importTemplate(importTemplateModal);
                bootbox.hideAll();
            }
        });
        jQuery('#importTemplate').on('click', function () {
            selectTemplate.find('option').remove().end().append('<option value="">-- Pick a Template --</option>').val('');
            jQuery.ajax({
                type: "GET",
                url: "/templates",
                contentType: "application/json",
                success: function (response) {
                    templates = response.data;
                    $.each(templates, function (i, template) {
                        selectTemplate.append($('<option>', {
                            value: template.pk,
                            text: template.__str__
                        }));
                    });
                },
                error: function(r) {
                    console.log(r);
                }
            });
            bootbox
                .dialog({
                    title: 'Import Template',
                    message: importTemplateModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(importTemplateModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(importTemplateModal);
                })
                .modal('show');
        });

        var createObjectInput = jQuery("#new-object-name-input");
        var createObjectModal = jQuery('#createObjectModal');
        createObjectModal.validate({
            rules: {
                name: {
                    required: true
                }
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                name: {
                    required: "Please enter a name"
                }
            },
            submitHandler: function (form) {
                createObjectNode(createObjectModal);
                bootbox.hideAll();
            }
        });
        jQuery('#createObject').on('click', function () {
            var node = getCurrentNode();
            loadUploader(createObjectModal.find('.file-uploader')[0]);
            createObjectModal
                .find('[name="name"]').val('').end()
                .find('[name="description"]').val('').end()
                .find('[name="tense"]').val(FUTURE_TENSE).prop("disabled", true).end()
                .find('[name="public"]').prop("checked", false).end();

            bootbox
                .dialog({
                    title: 'Create Artifact',
                    message: createObjectModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(createObjectModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(createObjectModal);
                })
                .modal('show');
            createObjectInput.focus();
        });

        var realizeObjectModal = jQuery('#realizeObjectModal');
        var realizeObjectSelectTense = realizeObjectModal
                .find('[name="tense"]');
        var realizeObjectInput = jQuery('#realize-object-name-input');
        realizeObjectModal.validate({
            ignore: "",
            rules: {
                name: {
                    required: true
                }
                //resource: {
                //    required: true
                //}
            },
            errorClass: "control-label",
            highlight: highlight,
            success: success,
            messages: {
                name: {
                    required: "Please enter a name"
                }
                //resource: {
                //    required: "A file is required"
                //}
            },
            submitHandler: function (form) {
                editObjectNode(realizeObjectModal);
                bootbox.hideAll();
                objectRealizationManager.updateObjects(getCurrentNode().key);
                objectRealizationManager.objectsAlreadyShown.push(myDiagram.findNodeForKey(getCurrentNode().key));
                objectRealizationManager.run();
            }
        });
        jQuery('#realizeObject').on('click', function (event) {
            var node = getCurrentNode();
            realizeObjectSelectTense.find('option').remove().end();
            realizeObjectSelectTense.append($('<option>', {
                    value: PRESENT_TENSE,
                    text : "Present"
                }));
            realizeObjectSelectTense.val(node.tense);
            var resource = (node.resourceName != undefined) ? "<a>" + node.resourceName + "</a>" : "";
            loadUploader(realizeObjectModal.find('.file-uploader')[0]);
            realizeObjectModal
                .find('[name="name"]').val(node.name).end()
                .find('[name="description"]').end()
                .find('[name="tense"]').val(PRESENT_TENSE).prop('disabled', true).end()
                .find('[class="file-name"]').html(resource)
                .find('[name="public"]').prop("checked", node.public == "YES").end();
            insertFileInput(realizeObjectModal.find('[class="file-input"]'),
                "resource", node.resourcePk != undefined ? node.resourcePk + RESOURCE_PK_NAME_SEPARATOR + node.resourceName : "");
            bootbox
                .dialog({
                    title: 'Realize Artifact',
                    message: realizeObjectModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        objectRealizationManager.reset();
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(realizeObjectModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(realizeObjectModal);
                })
                .modal('show');
            realizeObjectInput.focus();
        });

        var archiveNode = function(event) {
            var node = getCurrentNode();
            bootbox.confirm("Are you sure you want to archive this node?", function(r) {
                if (r) {
                    myDiagram.startTransaction("archiveNode");
                    updateNode(node, {
                        'fill': node.category == "Object" ? GREY_BLUE : GREY_YELLOW,
                        'tense': PAST_TENSE,
                        'fromLinkable': false,
                        'toLinkable': false,
                        'strokeDashArray': null,
                        'editable': false,
                        'textColor': 'white'
                    });
                    var outGoingEdges = 0;
                    myDiagram.selection.first().linksConnected.each(function(b) {
                        if (b.part.data.to != getCurrentNode().key) {
                            outGoingEdges++;
                        }
                    });
                    if (outGoingEdges == 0) {
                        var endNode = {
                            key: getKey(),
                            category: "End",
                            type: "E",
                            group: node.group,
                            createdBy: current_user.username,
                            loc: (myDiagram.toolManager.contextMenuTool.mouseDownPoint.x).toString() + " " + (100 + myDiagram.toolManager.contextMenuTool.mouseDownPoint.y).toString(),
                            date: getDate(),
                            is_modified: true
                        };
                        myDiagram.model.addNodeData(endNode);
                        myDiagram.model.addLinkData({
                            category: "Edge",
                            from: node.key,
                            to: endNode.key
                        });
                    }
                    myDiagram.commitTransaction("archiveNode");
                }
            }).on('hide.bs.modal', function (e) {
                myDiagram.toolManager.contextMenuTool.stopTool();
            })
        };

        jQuery('#archiveAction').on('click', archiveNode);
        jQuery('#archiveObject').on('click', archiveNode);

        jQuery('#deleteAction').on('click', deleteNode);
        jQuery('#deleteObject').on('click', deleteNode);
        jQuery('#deleteComment').on('click', deleteNode);

        jQuery('#synchronize').on('click', synchronize);

        jQuery('#undoDeleteAction').on('click', undoDeleteNode);
        jQuery('#undoDeleteObject').on('click', undoDeleteNode);
        jQuery('#undoDeleteComment').on('click', undoDeleteNode);

        var exportObjectsInput = jQuery('#export-objects-name-input');
        var exportObjectsModal = jQuery('#exportObjectsModal');
        var selectGroup = exportObjectsModal
                .find('[name="group"]');
        exportObjectsModal.validate({
            rules: {
                name: {
                    required: true,
                    minlength: 2
                }
            },
            errorClass: "control-label",
            highlight: function (element) {
                $(element).closest('.form-group')
                .removeClass('has-success').addClass('has-error');
            },
            success: function (element) {
                element.addClass('valid').closest('.form-group')
                .removeClass('has-error').addClass('has-success');
                element.closest('.control-label').remove();
            },
            messages: {
                name: {
                    required: "Please enter a package title",
                    minlength: "A package title must consist of at least 2 characters"
                }
            },
            submitHandler: function (form) {
                exportObjects(exportObjectsModal);
                bootbox.hideAll();
            }
        });
        jQuery('#exportObjects').on('click', function () {
            exportObjectsModal
                .find('[name="name"]').val("").end()
                .find('[name="description"]').val("").end()

            bootbox
                .dialog({
                    title: 'Export Artifacts',
                    message: exportObjectsModal,
                    show: false,
                    "animate": false,
                    onEscape: function () {
                        this.trigger('hide.bs.modal');
                    }
                })
                .on('shown.bs.modal', function () {
                    showModal(exportObjectsModal);
                })
                .on('hide.bs.modal', function (e) {
                    hideModal(exportObjectsModal);
                })
                .modal('show');
            exportObjectsInput.focus();
        });

        jQuery('#object-download').click(function (val) {
            if (!(myDiagram.currentTool instanceof go.ContextMenuTool)) return;
            var node = getCurrentNode();
            var downloadUrl = "/resources/" + node.resourcePk + "/download";
            jQuery.fileDownload(downloadUrl, {
                successCallback: function (url) {
                    console.log('You just got a file download dialog or ribbon for this URL :' + url);
                },
                failCallback: function (html, url) {
                    alert('Your file download has failed for this URL:' + url + '\r\n' +
                        'Please contact the system administrator for more details'
                    );
                }
            });
            myDiagram.currentTool.stopTool();
        });
        jQuery('#color_picker').ColorPicker({
            closeOnOutside: true,
            onSubmit: function(hsb, hex, rgb, el) {
                jQuery(el).val('#' + hex);
                jQuery(el).ColorPickerHide();
            },
            onBeforeShow: function () {
                jQuery(this).ColorPickerSetColor(this.value);
            },
            onShow: function (colpkr) {
                jQuery(colpkr).fadeIn(500);
                return false;
            },
            onHide: function (colpkr) {
                jQuery(colpkr).fadeOut(500);
                return false;
            },
            onChange: function (hsb, hex, rgb) {
                $('#color_picker div').css('backgroundColor', '#' + hex);
            }
        }).bind('keyup', function(){
            jQuery(this).ColorPickerSetColor(this.value);
        });

        jQuery('#grid').change(function() {
            myDiagram.startTransaction("grid");
            myDiagram.grid.visible = this.checked;
            myDiagram.commitTransaction("grid");
        });

        jQuery('#snap').change(function() {
            if (this.checked) {
                myDiagram.toolManager.draggingTool.isGridSnapEnabled = true;
                myDiagram.toolManager.resizingTool.isGridSnapEnabled = true;
            } else {
                myDiagram.toolManager.draggingTool.isGridSnapEnabled = false;
                myDiagram.toolManager.resizingTool.isGridSnapEnabled = false;
            }
        });

        jQuery('#align-left').click(function() {
            myDiagram.commandHandler.alignLeft();
        });

        jQuery('#align-right').click(function() {
            myDiagram.commandHandler.alignRight();
        });

        jQuery('#selectAllNodes').click(function() {
            collection = [];
            myDiagram.nodes.each(function(n) {
                if (n.part.data.group == getCurrentNode().key) {
                    collection.push(n);
                }
            });
            myDiagram.clearSelection();
            if (collection.length > 0) {
                myDiagram.selectCollection(collection);
            }
            myDiagram.toolManager.contextMenuTool.stopTool();
        });
    });
    return {
        "deleteNode": deleteNode,
        "objectRealizationManager": objectRealizationManager,
        "getLoc": getLoc
    };
});