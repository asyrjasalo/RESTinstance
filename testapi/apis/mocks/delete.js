function(request, state, logger, callback) {

  const proxy = require(`${process.cwd()}/apis/mocks/proxy.js`);

  proxy.fetch_response(request, state, logger, response => {
    if (response.statusCode != 200 && response.statusCode != 201) {
      response = {
        statusCode: 404,
        body: { "error": "Not found" }
      }
    }
    else {
      response = {
        statusCode: 204,
        body: response.body
      }
      state.responses[request.path] = response;
    }
    callback(response);
  });

}
