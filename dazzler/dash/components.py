from datetime import datetime
from typing import Optional

import dash
import dash_bootstrap_components as dbc


def event_source_id() -> str:
    """Extract the ID of the UI component that triggered the current
    event. This function should only be called inside a Dash callback
    handler.

    Returns:
        The (string) ID of the component or the empty string if the
        component couldn't be determined.
    """
    try:
        prop_id = dash.callback_context.triggered[0]['prop_id']
    except (IndexError, KeyError):
        prop_id = ''
    return prop_id.split('.')[0]

    # NOTE. No, apparently in Dash 2.3 (the one we've got) there isn't
    # a better way of doing this. In fact, the docs suggest to use this
    # horrendous one liner
    #
    #   dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    #
    # But Dash 2.4 sort of fixed the horror, so you can just query
    # `ctx.triggered_id`.
    # See:
    # - https://dash.plotly.com/determining-which-callback-input-changed

    # TODO. Replace above code w/ `ctx.triggered_id` when upgrading to
    # Dash 2.4.


def has_triggered(component_id: str) -> bool:
    """Has the given component triggered the current UI callback?
    This function should only be called inside a Dash callback handler.

    Args:
        component_id: the ID of the component to test.

    Returns:
        `True` for yes, `False` for no.
    """
    return event_source_id() == component_id


def datetime_local_input(component_id: str) -> dbc.Input:
    """Build a date-time picker component.

    Args:
        component_id: the ID to assign to the component.

    Returns:
        An Dash Bootstrap `Input` component with a type of `datetime-local`.
    """
    return dbc.Input(id=component_id, type='datetime-local')

    # NOTE. 'datetime-local' type. It's part of HTML 5 and works in most
    # recent browsers. It looks like it's a better option than Dash's own
    # picker which only lets you pick a day but not a time of the day.
    # See:
    # - https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local
    # - https://caniuse.com/?search=datetime-local


def from_datetime_local_input(value: Optional[str]) -> Optional[datetime]:
    """Parse the value of a datetime local input field.

    Args:
        value: the field's value.

    Returns:
        The parsed `datetime` object if the input string is valid, `None`
        otherwise.
    """
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None
