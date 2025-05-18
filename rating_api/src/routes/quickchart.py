"""
Helper functions for QuickChart API.
"""


class QuickChartDataItem:
    """
    A data item for the QuickChart API.
    """

    def __init__(self, title: str, rating: float):
        """
        Initialize a QuickChartDataItem instance.
        :param title: The title of the movie.
        :param rating: The rating of the movie.
        """
        self.title = title
        self.rating = rating


def create_quickchart_config(movie_items: list[QuickChartDataItem]) -> dict[str, dict]:
    """
    Create a QuickChart configuration for a bar chart with movie ratings.
    :param movie_items: The list of movie items to include in the chart.
    :return: A dictionary representing the QuickChart configuration.
    """
    base_config = {
        "type": "bar",
        "data": {
            "labels": [],
            "datasets": [{
                "label": "Rating (out of 10)",
                "data": [],
                "backgroundColor": "rgba(75, 192, 192, 0.6)"
            }]
        },
    }

    # Populate the labels and data
    for item in movie_items:
        base_config["data"]["labels"].append(item.title)
        base_config["data"]["datasets"][0]["data"].append(item.rating)

    return base_config
