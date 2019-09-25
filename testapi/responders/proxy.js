module.exports.fetch_response = function(request, state, logger, callback) {

  var port = 8080;
  if (request.headers && request.headers['X-Testenv-Port']) {
      port = parseInt(request.headers['X-Testenv-Port'])
  }

  if (typeof state.instances === "undefined") {
    state.instances = [];
  }

  if (typeof state.instances[port] === "undefined") {
    state.instances[port] = {};
  }

  if (typeof state.instances[port].responses === "undefined") {
    state.instances[port].responses = {};
  }

  if (state.instances[port].responses[request.path]) {
    response = state.instances[port].responses[request.path]
    response.token = port;
    return callback(response);
  }

  const http = require("http");

  var path = request.path;
  if (Object.keys(request.query).length > 0) {
    const querystring = require("querystring");
    var path = path + '?' + querystring.stringify(request.query);
  }

  const options = {
    method: "get",
    hostname: "localhost",
    port: port,
    path: path
  };

  var origin_request = http.request(options, response => {
    var body = "";
    response.setEncoding("utf8");
    response.on("data", chunk => {
      body += chunk;
    });
    response.on("end", function() {
      response.body = body;
      response.token = port;
      callback(response);
    });
  });

  origin_request.end();
}
