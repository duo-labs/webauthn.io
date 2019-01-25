var gulp = require('gulp');
var through2 = require('through2');
var log = require('fancy-log');

var sass = require('gulp-sass');
var sourcemaps = require('gulp-sourcemaps');
var autoprefixer = require('gulp-autoprefixer');

var sassInput = './static/src/scss/*.scss';
var sassOutput = './static/dist/css/';

var imagesInput = './static/src/images/*';
var imagesOutput = './static/dist/images/';

var fontsInput = "./static/src/fonts/**/*";
var fontsOutput = "./static/dist/fonts/"

var autoprefixerOptions = {
    browsers: ['last 2 versions', '> 5%', 'Firefox ESR']
};

const isProd = process.env.NODE_ENV === 'production';

var sassOptions = {
    errLogToConsole: true,
    outputStyle: isProd ? 'compressed' : 'expanded'
};


gulp.task('sass', function () {
    return gulp
        .src(sassInput)
        .pipe(isProd ? () => through2.obj() : sourcemaps.init())
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(isProd ? () => through2.obj() : sourcemaps.write())
        .pipe(autoprefixer(autoprefixerOptions))
        .pipe(gulp.dest(sassOutput))
});

gulp.task('images', () => {
    return gulp
        .src(imagesInput)
        .pipe(gulp.dest(imagesOutput))

});

gulp.task('fonts', () => {
    return gulp
        .src(fontsInput)
        .pipe(gulp.dest(fontsOutput))
});

gulp.task('sass-watch', function () {
    return gulp
        // Watch the input folder for change,
        // and run `sass` task when something happens
        .watch(sassInput, ['sass'])
        // When there is a change,
        // log a message in the console
        .on('change', function (event) {
            log('File ' + event.path + ' was ' + event.type + ', running tasks...');
        });
});

gulp.task('images-watch', ['images'], () => {
    return gulp
        .watch(imagesInput, ['images'])
        .on('change', event => {
            log(`File ${event.path} was ${event.type}`);
        })
})

gulp.task('watch', ['sass-watch', 'images-watch', 'fonts']);


gulp.task('build', ['sass', 'images', 'fonts']);

gulp.task('prod', function () {
    return gulp
        .src(sassInput)
        .pipe(sass({
            outputStyle: 'compressed'
        }))
        .pipe(autoprefixer(autoprefixerOptions))
        .pipe(gulp.dest(sassOutput));
});