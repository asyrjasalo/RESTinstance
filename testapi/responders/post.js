function(request, state, logger, callback) {

  if (!request.body) return {};

  var propertyId = "id";

  var params = JSON.parse(request.body);
  if (!params[propertyId]) {
    return {
      body: { "error": "No property '" + propertyId + "' given" }
    }
  }

  request.path = request.path + '/' + params[propertyId];

  const proxy = require(`${process.cwd()}/testapi/responders/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode == 200 || response.statusCode == 201) {
      response = {
        statusCode: 404,
        body: { "error": "Already exists" }
      }
    }
    else {
      const token = response.token;
      response = {
        statusCode: 201,
        body: request.body
      }
      state.instances[token].responses[request.path] = response;
    }
    callback(response);
  });

}
