define(['go', 'bootbox.min', 'main', 'file-saver.min', 'Blob', 'modals', 'fileuploader', 'underscore-min', 'jquery-ui.min', 'jquery.validate', 'additional-methods.min',], function(go, bootbox, alertify, saveAs, BB, modals) {
    require(['DrawCommandHandler'], function () {
        var HORIZONTAL = false;
        var MINLENGTH = 800;
        var MINBREADTH = 300;
        var lastStroked = null;
        var eventNodeSize = 42;
        var eventNodeInnerSize = eventNodeSize - 6;
        var eventNodeSymbolSize = eventNodeInnerSize - 14;
        var EventEndOuterFillColor = "pink";
        var EventSymbolLightFill = "white";
        var EventSymbolDarkFill = "dimgray";
        var EventDimensionStrokeColor = "green";
        var EventDimensionStrokeEndColor = "red";
        var eventNodeStrokeWidthIsEnd = 4;
        var MESSAGE_TYPE_ERROR = 0;
        var MESSAGE_TYPE_SUCCESS = 1;
        var MIN_NODE_DISTANCE = 70;

        function getSelectionCategory() {
            var category = "None";
                switch (myDiagram.selection.count) {
                    case 0:
                        category = "Diagram";
                        break;
                    case 1:
                        category = myDiagram.selection.first().category;
                        break;
                    default:
                        var onlyObjectNodes = myDiagram.selection.all( function(n) {
                            return n.part.data.category=="Object";
                        });
                        if (onlyObjectNodes && myDiagram.selection.count > 1) {
                            category = "Objects";
                            break;
                        } else {
                            var it = myDiagram.selection.iterator;
                            while (it.next()) {
                                if ((it.key.category == "Object" ||
                                    it.key.category.startsWith(ACTION_CATEGORY_PREFIX)) &&
                                    it.key.part.data.tense == FUTURE_TENSE) {
                                    category = "ActionsObjects";
                                } else if (it.key.category != "Object") {
                                    category = "None";
                                    break;
                                }
                            }
                            break;
                        }


                }
            return category;
        }

        function showMessage(s, type) {
            if (type == MESSAGE_TYPE_ERROR) {
                alertify.notify(s, 'error', 5, function () {
                });
            } else {
                alertify.notify(s, 'success', 5, function () {
                });
            }
        };

        function getDate() {
            var today = new Date();
            var dd = today.getDate();
            var mm = today.getMonth() + 1;
            var yyyy = today.getFullYear();
            if (dd < 10) {
                dd = '0' + dd
            }
            if (mm < 10) {
                mm = '0' + mm
            }
            return yyyy + '-' + mm + '-' + dd;
        }

        // this may be called to force the lanes to be laid out again
        function relayoutLanes() {
            myDiagram.nodes.each(function(lane) {
            if (!(lane instanceof go.Group)) return;
                if (lane.category === "Pool") return;
                lane.layout.isValidLayout = false;  // force it to be invalid
            });
            myDiagram.layoutDiagram();
        }

        // this is called after nodes have been moved or lanes resized, to layout all of the Pool Groups again
        function relayoutDiagram() {
            myDiagram.layout.invalidateLayout();
            myDiagram.findTopLevelGroups().each(function(g) { if (g.category === "Pool") g.layout.invalidateLayout(); });
            myDiagram.layoutDiagram();
        }

        // compute the minimum size of a Pool Group needed to hold all of the Lane Groups
        function computeMinPoolSize(pool) {
            // assert(pool instanceof go.Group && pool.category === "Pool");
            var len = MINLENGTH;
            pool.memberParts.each(function(lane) {
            // pools ought to only contain lanes, not plain Nodes
            if (!(lane instanceof go.Group)) return;
                var holder = lane.placeholder;
                if (holder !== null) {
                    var sz = holder.actualBounds;
                    len = Math.max(len, sz.height);
                }
            });
            return new go.Size(NaN, len);
        }

    // compute the minimum size for a particular Lane Group
    function computeLaneSize(lane) {
        // assert(lane instanceof go.Group && lane.category !== "Pool");
        var sz = computeMinLaneSize(lane);
        if (lane.isSubGraphExpanded) {
            var holder = lane.placeholder;
            if (holder !== null) {
                var hsz = holder.actualBounds;
                sz.width = Math.max(sz.width, hsz.width);
            }
        }
        // minimum breadth needs to be big enough to hold the header
        var hdr = lane.findObject("HEADER");
        sz.width = Math.max(sz.width, hdr.actualBounds.width);
        return sz;
    }

    // determine the minimum size of a Lane Group, even if collapsed
    function computeMinLaneSize(lane) {
        if (!lane.isSubGraphExpanded) return new go.Size(1, MINLENGTH);
        return new go.Size(MINBREADTH, MINLENGTH);
    }


    // define a custom ResizingTool to limit how far one can shrink a lane Group
    function LaneResizingTool() {
        go.ResizingTool.call(this);
    }
    go.Diagram.inherit(LaneResizingTool, go.ResizingTool);

    LaneResizingTool.prototype.isLengthening = function() {
      return (this.handle.alignment === go.Spot.Bottom);
    };

  /** @override */
    LaneResizingTool.prototype.computeMinPoolSize = function() {
        var lane = this.adornedObject.part;
    // assert(lane instanceof go.Group && lane.category !== "Pool");
        var msz = computeMinLaneSize(lane);  // get the absolute minimum size
        if (this.isLengthening()) {  // compute the minimum length of all lanes
            var sz = computeMinPoolSize(lane.containingGroup);
            msz.height = Math.max(msz.height, sz.height);
        } else {  // find the minimum size of this single lane
            var sz = computeLaneSize(lane);
            msz.width = Math.max(msz.width, sz.width);
            msz.height = Math.max(msz.height, sz.height);
        }
        return msz;
    };

  /** @override */
    LaneResizingTool.prototype.resize = function(newr) {
        var lane = this.adornedObject.part;
        if (this.isLengthening()) {  // changing the length of all of the lanes
            lane.containingGroup.memberParts.each(function(lane) {
                if (!(lane instanceof go.Group)) return;
                    var shape = lane.resizeObject;
                    if (shape !== null) {  // set its desiredSize length, but leave each breadth alone
                        shape.height = newr.height;
                    }
            });
        } else {  // changing the breadth of a single lane
            go.ResizingTool.prototype.resize.call(this, newr);
        }
        relayoutDiagram();  // now that the lane has changed size, layout the pool again
    };
    // end LaneResizingTool class


    // define a custom grid layout that makes sure the length of each lane is the same
    // and that each lane is broad enough to hold its subgraph
    function PoolLayout() {
        go.GridLayout.call(this);
        this.cellSize = new go.Size(1, 1);
        this.wrappingColumn = Infinity;
        this.wrappingWidth = Infinity;
        this.isRealtime = false;  // don't continuously layout while dragging
        this.alignment = go.GridLayout.Position;
        // This sorts based on the location of each Group.
        // This is useful when Groups can be moved up and down in order to change their order.
        this.comparer = function(a, b) {
            var ax = a.location.x;
            var bx = b.location.x;
            if (isNaN(ax) || isNaN(bx)) return 0;
            if (ax < bx) return -1;
            if (ax > bx) return 1;
            return 0;
        };
    }
  go.Diagram.inherit(PoolLayout, go.GridLayout);

  /** @override */
    PoolLayout.prototype.doLayout = function(coll) {
        var diagram = this.diagram;
        if (diagram === null) return;
        diagram.startTransaction("PoolLayout");
        var pool = this.group;
        if (pool !== null && pool.category === "Pool") {
        // make sure all of the Group Shapes are big enough
            var minsize = computeMinPoolSize(pool);
            pool.memberParts.each(function(lane) {
                if (!(lane instanceof go.Group)) return;
                if (lane.category !== "Pool") {
                    var shape = lane.resizeObject;
                    if (shape !== null) {  // change the desiredSize to be big enough in both directions
                        var sz = computeLaneSize(lane);
                        shape.width = (!isNaN(shape.width)) ? Math.max(shape.width, sz.width) : sz.width;
                        shape.height = (isNaN(shape.height) ? minsize.height : Math.max(shape.height, minsize.height));
                        var cell = lane.resizeCellSize;
                        if (!isNaN(shape.width) && !isNaN(cell.width) && cell.width > 0) shape.width = Math.ceil(shape.width / cell.width) * cell.width;
                        if (!isNaN(shape.height) && !isNaN(cell.height) && cell.height > 0) shape.height = Math.ceil(shape.height / cell.height) * cell.height;
                    }
                }
            });
        }
    // now do all of the usual stuff, according to whatever properties have been set on this GridLayout
    go.GridLayout.prototype.doLayout.call(this, coll);
    diagram.commitTransaction("PoolLayout");
    };
    // end PoolLayout class
        var infoBoxH = document.getElementById("infoBoxHolder");

        function updateInfoBox(mousePt, data) {
            var infobox = "<div id='infoBox'>";
            if (data.description != undefined &&
                data.description != "" &&
                data.description != null) {
                infobox += "<textarea disabled style='resize: none; overflow: hidden;' rows=4'>"
                + data.description.substring(0, 100) + (data.description.length > 100 ? "..." : "") + "</textarea>";
            }
            infobox += "<div>" + data.createdBy + "</div>" +
            "<div >" + data.date + "</div></div>";
            infoBoxH.innerHTML = infobox;
            infoBoxH.style.left = mousePt.x + 40 + "px";
            infoBoxH.style.top = mousePt.y - 40 + "px";
        }

        function refreshTitle() {
            var currentFile = document.getElementById("currentFile");
            var idx = currentFile.textContent.indexOf("*");
            if (myDiagram.isModified) {
                myDiagram.model.addChangedListener(function (e) {
                    if ([
                            "loc",
                            "name",
                            "tense",
                            "description",
                            "group",
                            "category",
                            "public",
                            "createdBy",
                            "width",
                            "height",
                            "points",
                            "from",
                            "to",
                            "resourcePk"
                        ].indexOf(e.propertyName) > -1 && e.object && e.oldValue != e.newValue) {
                        myDiagram.model.setDataProperty(e.object, 'is_modified', true);
                    }
                });
                if (idx < 0) currentFile.textContent = currentFile.textContent + "*";
            } else {
                if (idx >= 0) currentFile.textContent = currentFile.textContent.substr(0, idx);
            }
        };

        function init() {
            console.log("INIT STARTED!!!!");


            var $ = go.GraphObject.make;

            myDiagram =
      $(go.Diagram, "myDiagram",
        {
          // start everything in the middle of the viewport
          initialContentAlignment: go.Spot.Center,
          commandHandler: new DrawCommandHandler(),
          allowDrop: true,
          // use a custom ResizingTool (along with a custom ResizeAdornment on each Group)
          resizingTool: new LaneResizingTool(),
          // use a simple layout that ignores links to stack the top-level Pool Groups next to each other
          layout: $(PoolLayout),
          // don't allow dropping onto the diagram's background unless they are all Groups (lanes or pools)
          mouseDragOver: function(e) {
            if (!e.diagram.selection.all(function(n) { return n instanceof go.Group; })) {
              e.diagram.currentCursor = 'not-allowed';
            }
          },
          mouseDrop: function(e, grp) {
            if (!e.diagram.selection.all(function(n) { return n instanceof go.Group; })) {
                var ok = grp.addMembers(grp.diagram.selection, true);
                if (!ok) grp.diagram.currentTool.doCancel();
            }

          },
          // a clipboard copied node is pasted into the original node's group (i.e. lane).
          "commandHandler.copiesGroupKey": true,
          // automatically re-layout the swim lanes after dragging the selection
          "SelectionMoved": relayoutDiagram,  // this DiagramEvent listener is
          "SelectionCopied": relayoutDiagram, // defined above
          "animationManager.isEnabled": false,
          // enable undo & redo
          "undoManager.isEnabled": true
        });

function groupStyle() {  // common settings for both Lane and Pool Groups
      return [
        {
          layerName: "Background",  // all pools and lanes are always behind all nodes and links
          background: "transparent",  // can grab anywhere in bounds
          movable: true, // allows users to re-order by dragging
          copyable: false,  // can't copy lanes or pools
          avoidable: false,  // don't impede AvoidsNodes routed Links
          minLocation: new go.Point(-Infinity, NaN),  // only allow vertical movement
          maxLocation: new go.Point(Infinity, NaN)
        },
        new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify)
      ];
    }
            myDiagram.addDiagramListener("Modified", refreshTitle);
            function nodeStyle() {
                return [
                    new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify),
                    {
                        locationSpot: go.Spot.Center,
                        mouseEnter: function (e, obj) {
                            showPorts(obj.part, true);
                            if (e.diagram instanceof go.Palette) return;
                            timer = setTimeout(function () {
                                updateInfoBox(e.viewPoint, obj.data);
                            }, 1000);
                        },
                        mouseLeave: function (e, obj) {
                            showPorts(obj.part, false);
                            if (e.diagram instanceof go.Palette) return;
                            if (typeof timer !== 'undefined') {
                                clearTimeout(timer);
                            }
                            infoBoxH.innerHTML = '';
                        },
                        click: function (e, obj) {
                            showPorts(obj.part, false);
                            if (e.diagram instanceof go.Palette) return;
                            if (typeof timer !== 'undefined') {
                                clearTimeout(timer);
                            }
                            infoBoxH.innerHTML = '';
                        }
                    }
                ];
            }

            function makePort(name, spot, output, input, width, height) {
                return $(go.Shape, "Circle",
                    {
                        fill: "transparent",
                        stroke: null,
                        desiredSize: new go.Size(width, height),
                        alignment: spot,
                        alignmentFocus: spot,
                        portId: name,
                        fromSpot: spot,
                        toSpot: spot,
                        fromLinkable: output,
                        toLinkable: input,
                        cursor: "pointer"
                    },
                    new go.Binding("fromLinkable", "fromLinkable").makeTwoWay(),
                    new go.Binding("toLinkable", "toLinkable").makeTwoWay()
                );

            }

    // hide links between lanes when either lane is collapsed
    function updateCrossLaneLinks(group) {
      group.findExternalLinksConnected().each(function(l) {
        l.visible = (l.fromNode.isVisible() && l.toNode.isVisible());
      });
    }

    var commandHandler = myDiagram.commandHandler;
    commandHandler.pasteSelection = function(pos) {
        go.CommandHandler.prototype.pasteSelection.call(commandHandler);
        myDiagram.selection.each(function (el) {
            myDiagram.model.setDataProperty(el.part.data, "loc", modals.getLoc(el.part.data.loc, 100));
            myDiagram.model.setDataProperty(el.part.data, "pk", null);
            console.log("NULL!");
        });
    }

     myDiagram.groupTemplate =
      $(go.Group, "Vertical", groupStyle(),
        {
            contextMenu: $(go.Adornment),
          selectionObjectName: "SHAPE",  // selecting a lane causes the body of the lane to be highlit, not the label
          resizable: true, resizeObjectName: "SHAPE",  // the custom resizeAdornmentTemplate only permits two kinds of resizing
          // layout: $(go.LayeredDigraphLayout,  // automatically lay out the lane's subgraph
          //           {
          //             isInitial: false,  // don't even do initial layout
          //             isOngoing: false,  // don't invalidate layout when nodes or links are added or removed
          //             direction: 90,
          //             columnSpacing: 10,
          //             layeringOption: go.LayeredDigraphLayout.LayerLongestPathSource
          //           }),
          computesBoundsAfterDrag: true,  // needed to prevent recomputing Group.placeholder bounds too soon
          computesBoundsIncludingLinks: false,  // to reduce occurrences of links going briefly outside the lane
          computesBoundsIncludingLocation: true,  // to support empty space at top-left corner of lane
          mouseDrop: function(e, grp) {  // dropping a copy of some Nodes and Links onto this Group adds them to this Group
            // don't allow drag-and-dropping a mix of regular Nodes and Groups
            var ok = grp.addMembers(grp.diagram.selection, true);
            if (!ok || (grp instanceof go.Group && grp.diagram.selection.first() instanceof go.Group)) grp.diagram.currentTool.doCancel();
          },
          subGraphExpandedChanged: function(grp) {
            var shp = grp.resizeObject;
            if (grp.diagram.undoManager.isUndoingRedoing) return;
            if (grp.isSubGraphExpanded) {
              shp.width = grp._savedBreadth;
            } else {
              grp._savedBreadth = shp.width;
              shp.width = NaN;
            }
            updateCrossLaneLinks(grp);
          }
        },
        new go.Binding("isSubGraphExpanded", "expanded").makeTwoWay(),
        // the lane header consisting of a Shape and a TextBlock
        $(go.Panel, "Horizontal",
          { name: "HEADER",
            angle: 0,  // maybe rotate the header to read sideways going up
            alignment: go.Spot.Center },
          $(go.Panel, "Horizontal",  // this is hidden when the swimlane is collapsed
            new go.Binding("visible", "isSubGraphExpanded").ofObject(),
            $(go.TextBlock,  // the lane label
              { font: "bold 13pt sans-serif", editable: true, margin: new go.Margin(2, 0, 0, 0) },
              new go.Binding("text", "name").makeTwoWay())
          ),
          $("SubGraphExpanderButton", { margin: 5 })  // but this remains always visible!
        ),  // end Horizontal Panel
        $(go.Panel, "Auto",  // the lane consisting of a background Shape and a Placeholder representing the subgraph
          $(go.Shape, "Rectangle",  // this is the resized object
            { name: "SHAPE", fill: "white" },
            new go.Binding("fill", "color"),
            new go.Binding("width", "width").makeTwoWay(),
            new go.Binding("height", "height").makeTwoWay(),
            new go.Binding("desiredSize", "size", go.Size.parse).makeTwoWay(go.Size.stringify)),
          $(go.Placeholder,
            { padding: 12, alignment: go.Spot.TopLeft }),
          $(go.TextBlock,  // this TextBlock is only seen when the swimlane is collapsed
            { name: "LABEL",
              font: "bold 13pt sans-serif", editable: true,
              angle: 90, alignment: go.Spot.TopLeft, margin: new go.Margin(4, 0, 0, 2) },
            new go.Binding("visible", "isSubGraphExpanded", function(e) { return !e; }).ofObject(),
            new go.Binding("text", "name").makeTwoWay())
        )  // end Auto Panel
      );  // end Group

    // define a custom resize adornment that has two resize handles if the group is expanded
    myDiagram.groupTemplate.resizeAdornmentTemplate =
      $(go.Adornment, "Spot",
        $(go.Placeholder),
        $(go.Shape,  // for changing the length of a lane
          {
            alignment: go.Spot.Bottom,
            desiredSize: new go.Size(50, 7),
            fill: "lightblue", stroke: "dodgerblue",
            cursor: "row-resize"
          },
          new go.Binding("visible", "", function(ad) { return ad.adornedPart.isSubGraphExpanded; }).ofObject()),
        $(go.Shape,  // for changing the breadth of a lane
          {
            alignment: go.Spot.Right,
            desiredSize: new go.Size(7, 50),
            fill: "lightblue", stroke: "dodgerblue",
            cursor: "col-resize"
          },
          new go.Binding("visible", "", function(ad) { return ad.adornedPart.isSubGraphExpanded; }).ofObject())
      );

    myDiagram.groupTemplateMap.add("Pool",
      $(go.Group, "Auto", groupStyle(),
        { // use a simple layout that ignores links to stack the "lane" Groups next to each other
          layout: $(PoolLayout, { spacing: new go.Size(0, 0) })  // no space between lanes
        },
        $(go.Shape,
          { fill: "white" },
          new go.Binding("fill", "color")),
        $(go.Panel, "Table",
          { defaultRowSeparatorStroke: "black" },
          $(go.Panel, "Horizontal",
            { row: 0, angle: 0 },
            $(go.TextBlock,
              { font: "bold 16pt sans-serif", editable: true, margin: new go.Margin(2, 0, 0, 0) },
              new go.Binding("text", "name").makeTwoWay())
          ),
          $(go.Placeholder,
            { row: 1 })
        )
      ));
            myDiagram.nodeTemplateMap.add("Start",
                $(go.Node, "Spot", nodeStyle(),
                    $(go.Panel, "Auto",
                        $(go.Shape, "Circle",
                            {desiredSize: new go.Size(30, 30), fill: "black", stroke: null})
                    ),
                    makePort("L", go.Spot.Left, true, false, 5, 5),
                    makePort("R", go.Spot.Right, true, false, 5, 5),
                    makePort("B", go.Spot.Bottom, true, false, 5, 5)
                ));

            myDiagram.nodeTemplateMap.add("End",
                $(go.Node, "Spot", nodeStyle(),
                    $(go.Panel, "Auto",
                        $(go.Shape, "Circle",
                            {desiredSize: new go.Size(30, 30), fill: "white", strokeWidth: 2, stroke: "black"}),
                        $(go.Shape, "ThinX",
                            {desiredSize: new go.Size(15, 15), fill: "black", stroke: null})
                    ),
                    makePort("T", go.Spot.Top, false, true, 5, 5),
                    makePort("L", go.Spot.Left, false, true, 5, 5),
                    makePort("R", go.Spot.Right, false, true, 5, 5)
                ));

            myDiagram.nodeTemplateMap.add("Choice",
                $(go.Node, "Spot", nodeStyle(),
                    $(go.Panel, "Auto",
                        $(go.Shape, "Decision",
                            {desiredSize: new go.Size(30, 30), fill: "white", strokeWidth: 2, stroke: "black"})
                    ),
                    makePort("T", go.Spot.Top, false, true, 5, 5),
                    makePort("L", go.Spot.Left, true, true, 5, 5),
                    makePort("R", go.Spot.Right, true, true, 5, 5),
                    makePort("B", go.Spot.Bottom, true, false, 5, 5)
                ));

            myDiagram.nodeTemplateMap.add("Action-In",
                $(go.Node, "Spot", nodeStyle(),
                    {resizable: true, resizeObjectName:"INFO-SHAPE"},
                    $(go.Panel, "Auto",
                        $(go.Shape, "RoundedRectangle",
                            {
                                name: "INFO-SHAPE",
                                minSize: new go.Size(70, 40),
                                fill: "white",
                                strokeWidth: 2,
                                stroke: "black"
                            },
                            new go.Binding("strokeDashArray", "strokeDashArray").makeTwoWay(),
                            new go.Binding("fill", "fill").makeTwoWay(),
                            new go.Binding('width').makeTwoWay(),
                            new go.Binding('height').makeTwoWay()
                        ),
                        $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),
                        $(go.TextBlock,
                            {
                                font: "9pt Helvetica, Arial, sans-serif",
                                editable: true,
                                wrap: go.TextBlock.WrapFit,
                                isMultiline: true
                            },
                            new go.Binding("text", "name").makeTwoWay(),
                            new go.Binding("stroke", "textColor").makeTwoWay(),
                            new go.Binding("editable", "editable").makeTwoWay()),
                        {contextMenu: $(go.Adornment)}
                    ),
                    makePort("T", go.Spot.Top, false, true, 10, 10),
                    makePort("L", go.Spot.Left, true, true, 10, 10),
                    makePort("R", go.Spot.Right, true, true, 10, 10),
                    makePort("B", go.Spot.Bottom, true, false, 10, 10)
                ));

            myDiagram.nodeTemplateMap.add("Action-Im",
                $(go.Node, "Spot", nodeStyle(),
                    {resizable: true, resizeObjectName:"INFO-SHAPE"},
                    $(go.Panel, "Auto",
                        $(go.Shape,
                            {
                                geometryString: "F M0 0 L100 0 L100 100 L0 100 L20 50 L0 0z",
                                name: "INFO-SHAPE",
                                minSize: new go.Size(70, 40),
                                fill: "white",
                                strokeWidth: 2,
                                stroke: "black"
                            },
                            new go.Binding("strokeDashArray", "strokeDashArray").makeTwoWay(),
                            new go.Binding("fill", "fill").makeTwoWay(),
                            new go.Binding('width').makeTwoWay(),
                            new go.Binding('height').makeTwoWay()
                        ),
                        $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),
                        $(go.TextBlock,
                            {
                                font: "9pt Helvetica, Arial, sans-serif",
                                editable: true,
                                wrap: go.TextBlock.WrapFit,
                                isMultiline: true
                            },
                            new go.Binding("stroke", "textColor").makeTwoWay(),
                            new go.Binding("editable", "editable").makeTwoWay(),
                            new go.Binding("text", "name").makeTwoWay()),
                        {contextMenu: $(go.Adornment)}
                    ),
                    makePort("T", go.Spot.Top, false, true, 10, 10),
                    makePort("L", go.Spot.Left, true, true, 10, 10),
                    makePort("R", go.Spot.Right, true, true, 10, 10),
                    makePort("B", go.Spot.Bottom, true, false, 10, 10)
                ));

            myDiagram.nodeTemplateMap.add("Action-Ex",
                $(go.Node, "Spot", nodeStyle(),
                    {resizable: true, resizeObjectName:"INFO-SHAPE"},
                    $(go.Panel, "Auto",
                        $(go.Shape,
                            {
                                geometryString: "F M0 0 L100 0 L130 50 L100 100 L0 100 L0 0z",
                                name: "INFO-SHAPE",
                                minSize: new go.Size(70, 40),
                                fill: "white",
                                strokeWidth: 2,
                                stroke: "black"
                            },
                            new go.Binding("strokeDashArray", "strokeDashArray").makeTwoWay(),
                            new go.Binding("fill", "fill").makeTwoWay(),
                            new go.Binding('width').makeTwoWay(),
                            new go.Binding('height').makeTwoWay()
                        ),
                        $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),
                        $(go.TextBlock,
                            {
                                font: "9pt Helvetica, Arial, sans-serif",
                                editable: true,
                                wrap: go.TextBlock.WrapFit,
                                isMultiline: true
                            },
                            new go.Binding("stroke", "textColor").makeTwoWay(),
                            new go.Binding("editable", "editable").makeTwoWay(),
                            new go.Binding("text", "name").makeTwoWay()),
                        {contextMenu: $(go.Adornment)}
                    ),
                    makePort("T", go.Spot.Top, false, true, 10, 10),
                    makePort("L", go.Spot.Left, true, true, 10, 10),
                    makePort("R", go.Spot.Right, true, true, 10, 10),
                    makePort("B", go.Spot.Bottom, true, false, 10, 10)
                ));

            myDiagram.nodeTemplateMap.add("Object",
                $(go.Node, "Spot", nodeStyle(),
                    {resizable: true, resizeObjectName:"INFO-SHAPE"},
                    $(go.Panel, "Auto",
                        $(go.Shape, "File",
                            {
                                name: "INFO-SHAPE",
                                minSize: new go.Size(50, 60),
                                fill: "white",
                                strokeWidth: 2,
                                stroke: "black"
                            },
                            new go.Binding("strokeDashArray", "strokeDashArray").makeTwoWay(),
                            new go.Binding("fill", "fill").makeTwoWay(),
                            new go.Binding('width').makeTwoWay(),
                            new go.Binding('height').makeTwoWay()
                        ),
                        $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),

                        $(go.TextBlock,
                            {
                                font: "9pt Helvetica, Arial, sans-serif",
                                editable: true,
                                wrap: go.TextBlock.WrapFit,
                                margin: 2, width: 80,
                                wrap: go.TextBlock.WrapFit, textAlign: "center",
                                isMultiline: true,
                                stroke: 'black'
                            },
                            new go.Binding("text", "name").makeTwoWay(),
                            new go.Binding("editable", "editable").makeTwoWay(),
                            new go.Binding("stroke", "textColor").makeTwoWay()),
                        {contextMenu: $(go.Adornment)}
                    ),
                    makePort("R", go.Spot.Right, false, true, 10, 10),
                    makePort("L", go.Spot.Left, true, true, 10, 10),
                    makePort("T", go.Spot.Top, true, true, 10, 10),
                    makePort("B", go.Spot.Bottom, true, false, 10, 10)
                ))
            ;

            myDiagram.nodeTemplateMap.add("Fork",
                $(go.Node, "Auto", nodeStyle(),
                    $(go.Shape, "Rectangle",
                        {desiredSize: new go.Size(30, 10), fill: "black"}),
                    makePort("R", go.Spot.Right, true, true, 5, 5),
                    makePort("L", go.Spot.Left, true, true, 5, 5),
                    makePort("T", go.Spot.Top, true, true, 5, 5),
                    makePort("B", go.Spot.Bottom, true, true, 5, 5)
                ));

            myDiagram.nodeTemplateMap.add("Comment",
                $(go.Node, "Auto", nodeStyle(),
                    {resizable: true, resizeObjectName:"INFO-SHAPE"},
                    $(go.Shape, "File",
                        {name: "INFO-SHAPE", minSize: new go.Size(50, 30), fill: "yellow", stroke: null},
                        new go.Binding('width').makeTwoWay(),
                        new go.Binding('height').makeTwoWay()),
                    $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),
                    $(go.TextBlock,
                        {
                            margin: 5,
                            maxSize: new go.Size(200, NaN),
                            wrap: go.TextBlock.WrapFit,
                            textAlign: "center",
                            editable: true,
                            font: "bold 12pt Helvetica, Arial, sans-serif",
                            stroke: '#454545',
                            isMultiline: true
                        },
                        new go.Binding("text", "name").makeTwoWay()),
                    {
                        contextMenu: $(go.Adornment)
                    }
                ));

            myDiagram.linkTemplateMap.add("",
                $(go.Link,
                    {
                        routing: go.Link.AvoidsNodes,
                        curve: go.Link.JumpOver,
                        corner: 5, toShortLength: 4,
                        relinkableFrom: true,
                        relinkableTo: true,
                        reshapable: true
                    },
                    new go.Binding("points").makeTwoWay(),
                    new go.Binding("relinkableFrom").makeTwoWay(),
                    new go.Binding("relinkableTo").makeTwoWay(),
                    $(go.Shape,  // the link path shape
                        {isPanelMain: true, stroke: "black", strokeWidth: 2}),
                    $(go.Shape,  // the arrowhead
                        {toArrow: "standard", stroke: null, fill: "black"}),
                    $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()),
                    $(go.Panel, "Auto",  // the link label, normally not visible
                        {visible: false, name: "LABEL", segmentIndex: 2, segmentFraction: 0.5},
                        new go.Binding("visible", "visible").makeTwoWay(),
                        $(go.Shape, "RoundedRectangle",  // the label shape
                            {fill: "#F8F8F8", stroke: null}),
                        $(go.TextBlock, "Yes",  // the label
                            {
                                textAlign: "center",
                                font: "10pt Helvetica, Arial, sans-serif",
                                stroke: "#333333",
                                editable: true
                            },
                            new go.Binding("text", "name").makeTwoWay())
                    )
                )
            );

            myDiagram.linkTemplateMap.add("Sync",
                $(go.Link,
                    {
                        routing: go.Link.Normal,
                        curve: go.Link.JumpOver,
                        corner: 5, toShortLength: 4,
                        relinkableFrom: true,
                        relinkableTo: true,
                        reshapable: true
                    },
                    new go.Binding("points").makeTwoWay(),
                    $(go.Shape,  // the link path shape
                        {isPanelMain: true, stroke: "blue", strokeDashArray: [5,10], strokeWidth: 2}),
                    $(go.Picture, {
                                width: 30,
                                height: 30,
                                source: "/static/images/delete.png",
                                visible: false
                            },
                            new go.Binding("visible", "delete").makeTwoWay()
                        ),
                    $(go.Panel, "Auto",  // the link label, normally not visible
                        {visible: false, name: "LABEL", segmentIndex: 2, segmentFraction: 0.5},
                        new go.Binding("visible", "visible").makeTwoWay(),
                        $(go.Shape, "RoundedRectangle",  // the label shape
                            {fill: "#F8F8F8", stroke: null}),
                        $(go.TextBlock, "Yes",  // the label
                            {
                                textAlign: "center",
                                font: "10pt Helvetica, Arial, sans-serif",
                                stroke: "#333333",
                                editable: true
                            },
                            new go.Binding("text", "name").makeTwoWay())
                    )
                )
            );



            myDiagram.addDiagramListener("PartResized",
                function (e) {
                    e.diagram.selection.each(function (o) {
                        myDiagram.model.setDataProperty(o.part.data, 'width', o.actualBounds.width);
                        myDiagram.model.setDataProperty(o.part.data, 'height', o.actualBounds.height);
                    });
                });
            myDiagram.addDiagramListener("LinkDrawn",
                function (e) {
                    e.diagram.selection.each(function (o) {
                        if (o.part.data.category == undefined) {
                            myDiagram.model.setDataProperty(o.part.data, 'category', 'Edge');
                        }
                    });
                });
            var robot = new Robot(myDiagram);
            myDiagram.addDiagramListener("ObjectDoubleClicked",
                function (e) {
                    var o = e.diagram.selection.first();
                    if (o.part.data.category.startsWith(ACTION_CATEGORY_PREFIX)) {
                        jQuery("#editAction").click();
                    } else if (o.part.data.category == "Object") {
                        jQuery("#editObject").click();
                    } else if (o.part.data.category == "SwimLane") {
                        jQuery("#editSwimLane").click();
                    }
                });
            myDiagram.addDiagramListener("SelectionDeleting",
                function (e) {
                    if (e.diagram.selection.count > 1) {
                        e.cancel = true;
                        showMessage("Cannot delete multiple selected parts", MESSAGE_TYPE_ERROR);
                        return;
                    }
                    var o = e.diagram.selection.first();
                    if (((o.part.data.category == "Object" || o.part.data.category.startsWith(ACTION_CATEGORY_PREFIX)) &&
                        o.part.data.tense == FUTURE_TENSE) ||
                        o.part.data.category == "Comment") {
                        modals.deleteNode();
                    } else if (o.part.data.category =="Edge" || o.part.data.category == "Sync") {
                        if (myDiagram.model.findNodeDataForKey(o.part.data.to).tense != FUTURE_TENSE) {
                            e.cancel = true;
                            showMessage("Only flows leading to future tense nodes can be deleted", MESSAGE_TYPE_ERROR);
                        } else {
                            modals.deleteNode();
                        }
                    } else {
                        showMessage("Only nodes with future tense can be deleted", MESSAGE_TYPE_ERROR);
                    }
                    e.cancel = true;
                });


            myDiagram.addDiagramListener("ExternalObjectsDropped",
                function (e) {
                    var node = myDiagram.selection.first().part.data;
                    if (node.category.startsWith(ACTION_CATEGORY_PREFIX)) {
                        myDiagram.model.setDataProperty(node, 'operation_type', "In");
                    }
                    if (node.category.startsWith(ACTION_CATEGORY_PREFIX) || node.category == "Object") {
                        myDiagram.model.setDataProperty(node, 'tense', 0);
                        myDiagram.model.setDataProperty(node, 'strokeDashArray', [5, 10]);
                    }
                });
            function showLinkLabel(e) {
                modals.objectRealizationManager.reset();
                var label = e.subject.findObject("LABEL");
                if (label !== null) label.visible = (e.subject.fromNode.data.figure === "Diamond");
            }

            myPalette =
                $(go.Palette, "myPalette",
                    {
                        "animationManager.duration": 300,
                        nodeTemplateMap: myDiagram.nodeTemplateMap,
                        model: new go.GraphLinksModel([
                            {category: "Start", createdBy: current_user.username, date: getDate()},
                            {
                                category: ACTION_CATEGORY_PREFIX + OPERATION_TYPE_INTERNAL,
                                createdBy: current_user.username,
                                date: getDate()
                            },
                            {category: "Object", createdBy: current_user.username, date: getDate()},
                            {category: "Choice", createdBy: current_user.username, date: getDate()},
                            {category: "Fork", createdBy: current_user.username, date: getDate()},
                            {category: "End", createdBy: current_user.username, date: getDate()},
                            {category: "Comment", name: "", createdBy: current_user.username, date: getDate()},
                        ])
                    });

            // credits go to http://www.gojs.net/latest/samples/customContextMenu.html#
            var cxElement = document.getElementById("contextMenu");

            cxElement.addEventListener("contextmenu", function (e) {
                e.preventDefault();
                return false;
            }, false);
            cxElement.addEventListener("blur", function (e) {
                cxMenu.stopTool();
            }, false);

            var cxTool = myDiagram.toolManager.contextMenuTool;
            
            cxTool.setUpMenus = function () {
                cxTool.menus = [];
                this.objectEmptyCxMenu = this.objectEmptyCxMenu ? this.objectEmptyCxMenu : jQuery(".object-empty-cxmenu");
                this.objectNotExportedCxMenu = this.objectNotExportedCxMenu ? this.objectNotExportedCxMenu : jQuery(".object-not-exported-cxmenu");
                this.objectFutureCxMenu = this.objectFutureCxMenu ? this.objectFutureCxMenu : jQuery(".object-future-cxmenu");
                this.objectDeletedCxMenu = this.objectDeletedCxMenu ? this.objectDeletedCxMenu : jQuery(".object-deleted-cxmenu");
                this.objectPresentCxMenu = this.objectPresentCxMenu ? this.objectPresentCxMenu : jQuery(".object-present-cxmenu");
                this.actionFutureCxMenu = this.actionFutureCxMenu ? this.actionFutureCxMenu : jQuery(".action-future-cxmenu");
                this.actionDeletedCxMenu = this.actionDeletedCxMenu ? this.actionDeletedCxMenu : jQuery(".action-deleted-cxmenu");
                this.actionPresentCxMenu = this.actionPresentCxMenu ? this.actionPresentCxMenu : jQuery(".action-present-cxmenu");
                this.objectCxMenu = this.objectCxMenu ? this.objectCxMenu : jQuery(".object-cxmenu");
                this.objectsCxMenu = this.objectsCxMenu ? this.objectsCxMenu : jQuery(".objects-cxmenu");
                this.objectsActionsCxMenu = this.objectsActionsCxMenu ? this.objectsActionsCxMenu : jQuery(".objects-actions-cxmenu");
                this.swimLaneCxMenu = this.swimLaneCxMenu ? this.swimLaneCxMenu : jQuery(".swimlane-cxmenu");
                this.actionCxMenu = this.actionCxMenu ? this.actionCxMenu : jQuery(".action-cxmenu");
                this.graphCxMenu = this.graphCxMenu ? this.graphCxMenu : jQuery(".graph-cxmenu");
                this.commentCxMenu = this.commentCxMenu ? this.commentCxMenu : jQuery(".comment-cxmenu");
                this.commentDeletedCxMenu = this.commentDeletedCxMenu ? this.commentDeletedCxMenu : jQuery(".comment-deleted-cxmenu");
                this.menus.push(this.objectEmptyCxMenu);
                this.menus.push(this.objectNotExportedCxMenu);
                this.menus.push(this.objectFutureCxMenu);
                this.menus.push(this.objectDeletedCxMenu);
                this.menus.push(this.objectPresentCxMenu);
                this.menus.push(this.actionFutureCxMenu);
                this.menus.push(this.actionDeletedCxMenu);
                this.menus.push(this.actionPresentCxMenu);
                this.menus.push(this.objectCxMenu);
                this.menus.push(this.objectsCxMenu);
                this.menus.push(this.objectsActionsCxMenu);
                this.menus.push(this.swimLaneCxMenu);
                this.menus.push(this.actionCxMenu);
                this.menus.push(this.graphCxMenu);
                this.menus.push(this.commentCxMenu);
                this.menus.push(this.commentDeletedCxMenu);
            }

            cxTool.display = function (category) {
                if (category != "None") {
                    cxElement.style.display = "block";
                    var mousePt = this.diagram.lastInput.viewPoint;
                    cxElement.style.left = mousePt.x + 10 + "px";
                    cxElement.style.top = mousePt.y + 50 + "px";
                }
            }

            cxTool.hideContextMenu = function () {
                if (this.currentContextMenu === null) return;
                cxElement.style.display = "none";
                this.currentContextMenu = null;
            }

            cxTool.hideMenus = function () {
                _(this.menus).each(function(menu) {
                    menu.hide();
                });
            }
            cxTool.showContextMenu = function (contextmenu, obj) {
                if (this.diagram === null) return;
                var category = getSelectionCategory();
                if (contextmenu !== this.currentContextMenu) {
                    this.hideContextMenu();
                }
                this.setUpMenus();
                this.hideMenus();
                
                switch (category) {
                    case "Comment":
                        if (this.diagram.selection.first().part.data.delete == true) {
                            this.commentDeletedCxMenu.show();
                        } else {
                            this.commentCxMenu.show();
                        }
                        break;
                    case "Diagram":
                        this.currentContextMenu = contextmenu;
                        return;
                        break;
                    case "Objects": // Export
                        var objectsWithAttachedResource = 0;
                        var objectsWithNonFutureTense = 0;
                        this.diagram.selection.each(function (node) {
                            if (node.part.data.tense != FUTURE_TENSE) {
                                objectsWithNonFutureTense++;
                            }
                        });
                        this.objectsCxMenu.show();
                        if (objectsWithNonFutureTense == 0) {
                            this.objectsActionsCxMenu.show();
                        }
                        if (objectsWithAttachedResource != 0 && objectsWithNonFutureTense != 0) {
                             category = "None";
                        }
                        break;
                    case "ActionsObjects":
                        this.objectsActionsCxMenu.show();
                        break;
                    case "Object":
                        if (this.diagram.selection.first().part.data.resourceName != undefined) {
                            this.objectCxMenu.show();
                        } else { // Download should not be shown
                            this.objectEmptyCxMenu.show();
                        }
                        if (this.diagram.selection.first().part.data.public == "NO") {
                            this.objectNotExportedCxMenu.show();
                        }
                        if (this.diagram.selection.first().part.data.delete == true) {
                            this.objectDeletedCxMenu.show();
                        }
                        if (this.diagram.selection.first().part.data.tense == FUTURE_TENSE) { // Realize
                            this.objectFutureCxMenu.show();
                        }
                        if (this.diagram.selection.first().part.data.tense == PRESENT_TENSE) { // Archive
                            this.objectPresentCxMenu.show();
                        }
                        break;
                    case "SwimLane":
                        this.swimLaneCxMenu.show();
                        // if (this.diagram.)
                        break;
                    case ACTION_CATEGORY_PREFIX + OPERATION_TYPE_INTERNAL :
                    case ACTION_CATEGORY_PREFIX + OPERATION_TYPE_IMPORT :
                    case ACTION_CATEGORY_PREFIX + OPERATION_TYPE_EXPORT :
                        this.actionCxMenu.show();
                        if (this.diagram.selection.first().part.data.delete == true) {
                            this.actionDeletedCxMenu.show();
                        } else if (this.diagram.selection.first().part.data.tense == FUTURE_TENSE) { // Realize
                            this.actionFutureCxMenu.show();
                        } else if (this.diagram.selection.first().part.data.tense == PRESENT_TENSE) { // Archive
                            this.actionPresentCxMenu.show();
                        }
                        break;
                    case "Boundary":
                        //this.graphCxMenu.show();
                        this.currentContextMenu = contextmenu;
                        return;
                        break;
                    case "None":
                        break;
                }
                this.display(category);
                this.currentContextMenu = contextmenu;
            }

            var myOverview =
                $(go.Overview, "myOverview",
                    {observed: myDiagram, maxScale: 0.5, contentAlignment: go.Spot.Center});
            myOverview.box.elt(0).stroke = "dodgerblue";
            myOverview.toolManager.standardMouseWheel = function () {
                var observed = myOverview.observed;
                if (observed === null) return;
                var cmd = observed.commandHandler;

                var e = myOverview.lastInput;
                var delta = e.delta;
                if (delta === 0) return;

                if ((delta > 0 ? cmd.canIncreaseZoom() : cmd.canDecreaseZoom())) {
                    if (delta > 0)
                        cmd.increaseZoom();
                    else
                        cmd.decreaseZoom();
                    e.bubbles = false;
                }

            }
            load({message: false});

            console.log("INIT ENDED!!!!");
        }

        function showPorts(node, show) {
            var diagram = node.diagram;
            if (!diagram || diagram.isReadOnly || !diagram.allowLink) return;
            node.ports.each(function (port) {
                port.stroke = (show ? "white" : null);
                port.fill = show ? "rgba(0,0,0,.3)" : null;
            });
        }

        function save(params) {
            var obj = JSON.stringify(myDiagram.model.toJson());
            jQuery.ajax({
                type: "POST",
                url: "update/",
                contentType: "application/json",
                data: obj,
                success: function (response) {
                    myDiagram.isModified = false;
                    refreshTitle();
                    if (params.message) {
                        showMessage("Project successfully saved!", MESSAGE_TYPE_SUCCESS);
                    }
                    if (params.load) {
                        load({message: false});
                    }
                },
                error: function () {
                    showMessage("Project is NOT saved! An error occured.. Try to 'File->Export to JSON' your work and upload it later", MESSAGE_TYPE_ERROR);
                }
            });
        }

        function fixEdges(edges) {
            var newEdges = [];
            for (i = 0; i < edges.length; i++) {
                var newEdge = {};
                newEdge = {
                    "from": edges[i].src,
                    "to": edges[i].tgt,
                    "pk": edges[i].pk,
                    "points": JSON.parse(edges[i].points),
                    "category": edges[i].category,
                    "fromPort": edges[i].fromPort,
                    "toPort": edges[i].toPort
                };
                newEdges.push(newEdge);
            }
            return newEdges;
        }

        jQuery("#load-file").on("change", function(evt) {
            reader = new FileReader();
            reader.onerror = function() {
                showMessage("Error occured while parsing the uploaded file", MESSAGE_TYPE_ERROR);
            };
            reader.onabort = function(e) {
                showMessage("Operation aborted", MESSAGE_TYPE_ERROR);
            };
            reader.onload = function(e) {
                try {
                    var file = JSON.parse(e.target.result);
                    myDiagram.model = go.Model.fromJson(file);
                    showMessage("Project successfully loaded", MESSAGE_TYPE_SUCCESS);
                }
                catch(err) {
                    showMessage("Error occurred while parsing the uploaded file", MESSAGE_TYPE_ERROR);
                }
            };
            reader.readAsText(evt.target.files[0]);
        });

        function load(params) {
            jQuery.ajax({
                url: "load/",
                contentType: "application/json",
                success: function (response) {
                    myDiagram.isModified = false;
                    json = {
                        "class": "go.GraphLinksModel",
                        "linkFromPortIdProperty": "fromPort",
                        "linkToPortIdProperty": "toPort"
                    };
                    json.nodeDataArray = _(response.data.graphs[0].graph_elements).filter(function (d) {
                        return d.category != "Boundary" && d.category != "Edge" && d.category != "Sync"
                    });
                    json.linkDataArray = fixEdges(_(response.data.graphs[0].graph_elements).filter(function (d) {
                        return d.category == "Edge" || d.category == "Sync"
                    }));
                    myDiagram.model = go.Model.fromJson(json);
                    if (params.message) {
                        showMessage("Project successfully loaded", MESSAGE_TYPE_SUCCESS);
                    }
                    relayoutLanes();
                    modals.objectRealizationManager.reset();

                    // var nodeData = [
                    //    {"key":"Ioannis", "pk":2, "color":"Blue", "isGroup":true, "category":"SwimLane", "group":"Boundary"},
                    //    {"key":"Harald", "pk":3, "color":"Red", "isGroup":true, "category":"SwimLane", "group":"Boundary"},
                    //    {"key":"foo_4","pk":4, "name":"foo", "category":"Object", "public":"NO", "resourcePath":"Chrysanthemum.jpg", "resourceUrl":"TODO", "group":"Ioannis", "createdBy":"admin", "date":"2015-04-16", "loc":"50 51"},
                    //    {"key":"Renaming_5","pk":5, "category":"Action", "name":"Renaming", "description":"", "group":"Ioannis", "createdBy":"admin", "date":"2015-04-16", "loc":"50 147"},
                    //    {"key":"bar_6","pk":6, "name":"bar", "category":"Object", "public":"NO", "resourcePath":"Chrysanthemum.jpg", "resourceUrl":"http://localhost:8000/media/resources/Chrysanthemum.jpg", "group":"Ioannis", "createdBy":"admin", "date":"2015-04-16", "loc":"50 243"}
                    // ];
                    // var nodeData = _(response.data.graphs[0].graph_elements).filter(function(d) { return d.category!="Boundary" && d.category!="Flow"});
                    // var linkData = _(response.data.graphs[0].graph_elements).filter(function(d) { return d.category=="Flow"});
                    // _(response.data.graphs[0].graph_elements).filter(function(d) { return d.category=="Flow"});
                    // {"from":"foo_4", "to":"Renaming_5", "pk": 7, "points":[50,82,50,92,50,104.5,50,104.5,50,117,50,127]},
                    // {"from":"Renaming_5", "to":"bar_6","pk": 8, "points":[50,167,50,177,50,189.5,50,189.5,50,202,50,212]}
                    // myDiagram.model = new go.GraphLinksModel(
                    //    nodeData, linkData);
                }
            });
        }

        jQuery('#save').click(function () {
            save({message: true});
        });

        jQuery('#makeSvg').click(function () {
            var newWindow = window.open("", "newWindow");
            if (!newWindow) return;
            var newDocument = newWindow.document;
            var svg = myDiagram.makeSvg({
                document: newDocument,  // create SVG DOM in new document context
                scale: 1  // create SVG DOM in new document context
            });
            newDocument.body.appendChild(svg);
        });

        jQuery('#load').click(function () {
            load({message: true});
        });

        jQuery("#distribute-vertically").on('click', function () {
            var selectedOrderedNodes = _.chain(myDiagram.selection.toArray()).
                filter(function(n){ return n.category != "SwimLane" && n.category != ""; }).
                sortBy(function(n) { return n.location.y; }).
                value();
            if (selectedOrderedNodes.length > 2) {
                myDiagram.startTransaction("distribute-vertically");
                var curY = selectedOrderedNodes[0].location.y;
                var yIncrement = Math.max((selectedOrderedNodes[selectedOrderedNodes.length-1].location.y -
                    selectedOrderedNodes[0].location.y)/(selectedOrderedNodes.length - 1), MIN_NODE_DISTANCE);
                _.each(selectedOrderedNodes, function(node) {
                    myDiagram.model.setDataProperty(node.part.data, 'loc', node.location.x.toString() + " " + curY.toString());
                    curY = curY+yIncrement;
                }) ;
                relayoutDiagram();
                myDiagram.commitTransaction("distribute-vertically");
            }
        });

        // var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.parse(JSON.stringify(myDiagram.model.toJson());
        jQuery("#export-to-json").on("click", function() {
            saveAs(
                  new Blob(
                      [JSON.parse(JSON.stringify(myDiagram.model.toJson()))]
                    , {type: "text/json;charset=utf-8"}
                )
                , projectTitle + ".json"
            );
        });

        jQuery("#refresh").on('click', function() {
            if (myDiagram.isModified) {
                save({message: true, load: true});
            } else {
                load({message: true});
            }
        })
        init();
    });
});