from django.http import QueryDict

class HttpPostTunnelingMiddleware(object):
	def process_request(self, request):
		if request.META.has_key('HTTP_X_METHODOVERRIDE'):
			http_method = request.META['HTTP_X_METHODOVERRIDE']
			if http_method.lower() == 'put':
				request.method = 'put'
				request.META['REQUEST_METHOD'] = 'PUT'
				request.PUT = QueryDict(request.body)
			elif http_method.lower() == 'delete':
				request.method = 'delete'
				request.META['REQUEST_METHOD'] = 'DELETE'
				request.DELETE = QueryDict(request.body)
		return None	