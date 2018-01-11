function(request, state, logger, callback) {

  if (!request.body) return {};

  state.schema = JSON.parse(request.body);

  var response = {
      statusCode: 201,
      body: state.schema
  };

  callback(response);
}