#!/usr/bin/env python
from boxoffice import app, db

db.drop_all()
db.create_all()


@app.route('/testing')
def test_page() -> str:
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Buy tickets</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <script src='http://code.jquery.com/jquery-2.2.0.min.js'></script>
  <link rel="stylesheet"
    href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
  <link rel="stylesheet"
    href="http://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.5.0/css/font-awesome.css">
  <script src='http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js'>
  </script>
</head>
<body>
<div id='boxoffice-widget'></div>
<script>
    $.getScript("http://boxoffice.travis.dev:6500/api/1/boxoffice.js").done(function(){
      window.Boxoffice.init({
        org: 'rootconf',
        menu: '2016'
      });
    });
</script>
</body>
</html>"""


app.run('0.0.0.0', 6500, debug=True)  # nosec  # noqa: S104
