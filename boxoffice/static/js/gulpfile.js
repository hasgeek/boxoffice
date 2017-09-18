var gulp = require('gulp');
var fs = require('fs');
var browserify = require('browserify');
var watchify = require('watchify');
var babelify = require('babelify');
var source = require('vinyl-source-stream');
var uglify = require('gulp-uglify');
var streamify = require('gulp-streamify');
var _ = require('underscore');
var concat = require('gulp-concat');
var minify = require('gulp-minify-css');

configfiles = [{
    entryFile: './views/main_admin.js',
    outputFile: 'admin_bundle.js',
    destination: './dist'
  },
  {
    entryFile: './views/main_order.js',
    outputFile: 'order_bundle.js',
    destination: './dist'
  },
  {
    entryFile: './views/main_invoice.js',
    outputFile: 'invoice_bundle.js',
    destination: './dist'
  }
];

var isWatchify = false;

const createBundle = options => {
  let fileBundle = browserify(options.entry).transform(babelify);

  const rebundle = () =>
    fileBundle.bundle()
    // log errors if they happen
    .on('error', function(err) { console.log('Error: ' + err.message); })
    .pipe(source(options.output))
    .pipe(streamify(uglify()))
    .pipe(gulp.dest(options.destination));

  if (isWatchify) {
    fileBundle = watchify(fileBundle);
    fileBundle.on('update', rebundle);
  }

  return rebundle();
};

gulp.task('bundle_css', () =>
  gulp.src(['./node_modules/c3/c3.min.css','./node_modules/bootstrap-daterangepicker/daterangepicker.css', './node_modules/nprogress/nprogress.css'])
  .pipe(concat('admin_bundle.css'))
  .pipe(minify())
  .pipe(gulp.dest('../css/dist/'))
);

gulp.task('build', [], () => {
  configfiles.forEach( bundle =>
    createBundle({
      entry: bundle.entryFile,
      output: bundle.outputFile,
      destination: bundle.destination
    })
  );
  gulp.start('bundle_css');
});

gulp.task('watch', () => {
  isWatchify = true;
  gulp.start('build');
});
