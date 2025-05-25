from flask import render_template
from app import db

def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/error.html', 
                              code=404, 
                              title="Page Not Found", 
                              message="The page you're looking for doesn't exist."), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/error.html', 
                              code=403, 
                              title="Forbidden", 
                              message="You don't have permission to access this resource."), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/error.html', 
                              code=500, 
                              title="Internal Server Error", 
                              message="Something went wrong on our end. Please try again later."), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('errors/error.html', 
                              code=400, 
                              title="Bad Request", 
                              message="The server could not understand your request."), 400
