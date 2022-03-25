from blog.apps import create_app

app = create_app()
# 关键点，往celery推入flask信息，使得celery能使用flask上下文
app.app_context().push()
app.secret_key = '111'

if __name__ == '__main__':
    app.run(debug=True)
