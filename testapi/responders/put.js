function(request, state, logger, callback) {

  if (!request.body) return {};

  var propertyId = "id";

  var params = JSON.parse(request.body);
  if (params[propertyId]) {
    return {
      body: { "error": "Updating read-only parameter not allowed" }
    }
  }

  const proxy = require(`${process.cwd()}/testapi/responders/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode != 200 && response.statusCode != 201) {
      response = {
        statusCode: 404,
        body: { "error": "Not found" }
      }
    }
    else {
      var body = JSON.parse(response.body);
      Object.keys(params).forEach(property => {
        body[property] = params[property];
      });
      const token = response.token;
      response = {
        statusCode: 200,
        body: JSON.stringify(body)
      }
      state.instances[token].responses[request.path] = response;
    }
    callback(response);
  });

}
