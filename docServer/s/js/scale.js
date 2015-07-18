var nodeDataWithDate = _(myDiagram.model.nodeDataArray).filter(function (d) {
    return d.date;
});
function renderDateAxis()
{
    var margin = {top: 40, right: 40, bottom: 40, left: 40},
        width = 600,
        height = 500;

    var y = d3.time.scale()
        .domain([d3.time.day.offset(new Date(nodeDataWithDate[0].date), -1), d3.time.day.offset(new Date(nodeDataWithDate[nodeDataWithDate.length - 1].date), 1)])
        .rangeRound([10, myDiagramHeight]);

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient('left')
        .ticks(d3.time.days, 1)
        .tickFormat(d3.time.format('%a %d'));

    var svg = d3.select('#myDiagram').append('svg')
        .attr('id', 'dates')
        .attr('position', 'absolute')
        .attr('class', 'chart')
        .attr('width', width)
        .attr('height', myDiagramHeight)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');

    svg.append('g')
        .attr('class', 'y axis')
        .call(yAxis);
}
function scale() {

    myDiagram.layout.invalidateLayout();  // but don't invalidate all Layouts that are in Groups
    myDiagram.layoutDiagram();
    var y = d3.time.scale()
        .domain([d3.time.day.offset(new Date(nodeDataWithDate[0].date), -1), d3.time.day.offset(new Date(nodeDataWithDate[nodeDataWithDate.length - 1].date), 1)])
        .rangeRound([10, myDiagramHeight]);

    myDiagram.startTransaction("apply scale");
    _(nodeDataWithDate).each(
        function (d) {
            var node = myDiagram.findNodeForData(d);   // find the corresponding Node
            var p = node.location.copy();  // make a copy of the location, a Point
            p.y = y(new Date(d.date));
            node.location = p;
        }
    );
    myDiagram.commitTransaction("apply scale");
    $("#dates").remove();
    renderDateAxis();
}
var zoom = 0;
function zoomIn()
{
    myDiagramHeight = myDiagramHeight + 100;
    scale();
}

function zoomOut()
{
    myDiagramHeight = myDiagramHeight - 100;
    scale();
}