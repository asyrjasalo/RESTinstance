function(request, state, logger, callback) {

  if (!request.body) return {};

  var params = JSON.parse(request.body);
  if (params.id) {
    return {
      body: { "error": "Updating read-only parameter not allowed" }
    }
  }

  const proxy = require(`${process.cwd()}/apis/mocks/proxy.js`);

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
      response = {
        statusCode: 200,
        body: JSON.stringify(body)
      }
      state.responses[request.path] = response;
    }
    callback(response);
  });

}
