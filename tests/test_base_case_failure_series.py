def test___base_case__failure__series__in():
    """Test that the base case fails for series, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(se: Series[MySeriesFailure]) -> Series[MySeries]:
            return se

        my_function(se)


def test___base_case__failure__series__out():
    """Test that the base case fails for series, when output fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(se: Series[MySeries]) -> Series[MySeriesFailure]:
            return se

        my_function(se)


def test___base_case__failure__series__nested__in():
    """Test that the base case fails for series, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(
                se: tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeriesFailure]]]
        ) -> Series[MySeries]:
            return se

        my_function([se, [se, se]])


def test___base_case__failure__series__nested__out():
    """Test that the base case fails for series, when input is fails."""
    with pytest.raises(ValueError):
        @check_types
        def my_function(
                se: Series[MySeries],
        ) -> tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeriesFailure]]]:
            return [se, [se, se]]

        my_function(se)


def test___base_case__failure__series__mismatch_in__1():
    """Test that the base case fails for series, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(tup: tuple[Series[MySeries], Series[MySeries]]) -> Series[MySeries]:
            return tup[0]

        my_function(se)


def test___base_case__failure__series__mismatch_in__2(self):
    """Test that the base case fails for series, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(se: Series[MySeries]) -> Series[MySeries]:
            return se

        my_function((se, se))


def test___base_case__failure__series__mismatch_in__3():
    """Test that the base case fails for series, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(tup: tuple[Series[MySeries], Series[MySeries]]) -> Series[MySeries]:
            return tup[0]

        my_function((se, [se, se]))


def test___base_case__failure__series__mismatch_in__4():
    """Test that the base case fails for series, when input type hints do not match argument values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(
                nested_se: tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeries]]]
        ) -> Series[MySeries]:
            se, (se1, se2) = nested_se
            return se

        my_function((se, se, se))


def test___base_case__failure__series__mismatch_out__1():
    """Test that the base case fails for series, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(se: Series[MySeries]) -> tuple[Series[MySeries], Series[MySeries]]:
            return se

        my_function(se)


def test___base_case__failure__series__mismatch_out__2():
    """Test that the base case fails for series, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(se: Series[MySeries]) -> Series[MySeries]:
            return se, se

        my_function(se)


def test___base_case__failure__series__mismatch_out__3():
    """Test that the base case fails for series, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(se: Series[MySeries]) -> tuple[Series[MySeries], Series[MySeries]]:
            return se, [se, se]

        my_function(se)


def test___base_case__failure__series__mismatch_out__4():
    """Test that the base case fails for series, when output type hints do not match return values."""
    with pytest.raises(TypeError):
        @check_types
        def my_function(
                se: Series[MySeries],
        ) -> tuple[Series[MySeries], tuple[Series[MySeries], Series[MySeries]]]:
            return se, se, se

        my_function(se)
