from flask import request
from flask import session


class URL:
    @staticmethod
    def back():
        args = request.args.to_dict()

        # Scopes will be passed as mutliple args, and to_dict() will only
        # return one. So, we use getlist() to get all of the scopes.
        args['scopes'] = request.args.getlist('scopes')

        return_url = args.pop('return_url', None)

        if return_url is None:
            if 'previous_url' in session:
                return session['previous_url']

            return request.referrer or '/'

        return return_url