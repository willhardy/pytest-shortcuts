import os


def test_help_message(testdir):
    # Add the configuration from the readme
    testdir.makeini(
        """
        [pytest]
        shortcuts =
            --live: -m "live and not slow"
            --slow: -m "live and slow"
            --offline: --disable-socket -m "not live"
    """
    )

    result = testdir.runpytest("--help")
    result.stdout.fnmatch_lines(
        [
            "*--live*Shortcut for -m live and not slow",
        ]
    )
    result.stdout.fnmatch_lines(
        [
            "*shortcuts (linelist):*A colon-separated list of extra shortcut options*",
        ]
    )


def test_shortcuts_ini_setting(testdir):
    # Add the configuration from the readme
    testdir.makeini(
        """
        [pytest]
        markers =
            live: live
            slow: slow
        shortcuts =
            --live: -m "live and not slow"
            --slow: -m "live and slow"
            --offline: --disable-socket -m "not live"
    """
    )

    # Create a test that will run if it is selected with -m live
    # When the --live argument is expanded, it will only run marked tests
    testdir.makepyfile(
        """
        import pytest

        @pytest.fixture
        def marks(request):
            return request.config.getoption('-m')

        @pytest.mark.live
        def test_marks_set(marks):
            assert marks == 'live and not slow'
    """
    )

    # Provide the --live argument, which will be expanded to -m "live and not slow"
    result = testdir.runpytest("-v", "--live")

    result.stdout.fnmatch_lines(["*::test_marks_set PASSED*"])
    assert result.ret == 0


def test_envfiles_setting(testdir):
    # Add the configuration from the readme
    testdir.makeini(
        """
        [pytest]
        markers =
            live: live
            slow: slow
        shortcuts =
            --live: -m "live and not slow" --envfile=test.env
            --slow: -m "live and slow"
    """
    )
    testdir.makefile(".env", test="SPECIAL_ENV_VALUE=333")

    # Create a test that will run if it is selected with -m live
    # When the --live argument is expanded, it will only run marked tests
    testdir.makepyfile(
        """
        import pytest
        import os

        @pytest.mark.live
        def test_environment():
            assert os.getenv("SPECIAL_ENV_VALUE") == "333"
            del os.environ["SPECIAL_ENV_VALUE"]
    """
    )

    # Provide the --live argument, which will be expanded to -m "live and not slow"
    result = testdir.runpytest("-v", "--live")

    result.stdout.fnmatch_lines(["*::test_environment PASSED*"])
    assert result.ret == 0


def test_envfiles_deep(testdir):
    # Add the configuration from the readme
    testdir.makeini(
        """
        [pytest]
        markers =
            live: live
            slow: slow
        shortcuts =
            --live: -m "live and not slow" --envfile test.env
            --slow: -m "live and slow"
    """
    )
    testdir.makefile(".env", test="SPECIAL_ENV_VALUE=444")
    next_level = testdir.mkdir("next-level")

    # Create a test that will run if it is selected with -m live
    # When the --live argument is expanded, it will only run marked tests
    pyfile = testdir.makepyfile(
        """
        import pytest
        import os

        @pytest.mark.live
        def test_environment():
            assert os.getenv("SPECIAL_ENV_VALUE") == "444"
            del os.environ["SPECIAL_ENV_VALUE"]
    """
    )
    deep_pyfile = os.path.join(next_level, os.path.basename(pyfile))
    os.rename(pyfile, deep_pyfile)
    os.chdir(next_level)

    # Provide the --live argument, which will be expanded to -m "live and not slow"
    result = testdir.runpytest("-v", "--live")

    result.stdout.fnmatch_lines(["*::test_environment PASSED*"])
    assert result.ret == 0
