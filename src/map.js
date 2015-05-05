var width = 800,
    height = 800;

var projection = d3.geo.mercator()
    .center([20, 52])
    .scale(4000)
    .translate([400, 350]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var radius = d3.scale.sqrt()
    .range([0, 2]);

queue()
    .defer(d3.json, "../maps/poland.topo.json")
    .defer(d3.json, "../maps/readers_in_cities.json")
    .await(ready);

function ready(error, poland, circle) {
    svg.selectAll(".wojewodztwo")
        .data(topojson.feature(poland, poland.objects.poland_woj).features)
        .enter()
        .append("path")
        .attr("id", function(d) { return d.id; })
        .attr("d", path)
        .attr("class", "wojewodztwo");

    svg.selectAll(".symbol")
        .data(circle.features)
        .enter().append("path")
        .attr("class", "symbol")
        .attr("d", path.pointRadius(function(d) { return radius(d.properties.counter); }));
}