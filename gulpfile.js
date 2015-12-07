var gulp = require('gulp');
var watchLess = require('gulp-watch-less');
var less = require('gulp-less');
var bg = require("gulp-bg");
var Server = require('karma').Server;
var concat = require('gulp-concat');

var lessSrc = 'dashboard/static/css/app.less';
var lessDest = 'dashboard/static/css';

gulp.task("server", bg("python", "manage.py", "runserver", "0.0.0.0:8000"));
gulp.task("worker", bg("celery", "-A", "orderqualitytool.celery", "worker", "--loglevel=INFO", "--concurrency=6"));

gulp.task('default', ['server', 'worker'], function() {
    return gulp.src(lessSrc)
        .pipe(watchLess(lessSrc, function() {
            gulp.start('less');
        }));
});

gulp.task('scripts', function() {
    return gulp.src('dashboard/static/js/**/*.js')
        .pipe(concat('app.js'))
        .pipe(gulp.dest('dashboard/static/dist/'));
});

gulp.task('less', function() {
    return gulp.src(lessSrc)
        .pipe(less())
        .pipe(gulp.dest(lessDest));
});

gulp.task('test', function(done) {
    new Server({
        configFile: __dirname + '/karma.conf.js',
        singleRun: true
    }, done).start();
});

gulp.task('tdd', function(done) {
    new Server({
        configFile: __dirname + '/karma.conf.js',
        singleRun: false
    }, done).start();
});