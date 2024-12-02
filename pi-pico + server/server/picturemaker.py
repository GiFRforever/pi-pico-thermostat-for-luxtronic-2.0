import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colorbar import Colorbar

import matplotlib

matplotlib.use("agg")


def make_picture(
    path: str, name: str = "Teplota", min: float = 19, max: float = 23
) -> None:
    teploty: list[float] = []
    casy: list[str] = []

    with open(path, "r") as f:
        for line in f.readlines():
            try:
                cas, teplota = line.split(";")
                if cas in casy:
                    continue
                teploty.append(float(teplota))
                casy.append(cas)
            except ValueError:
                pass

    if casy[0] != "00:00":
        casy.insert(0, "00:00")
        teploty.insert(0, teploty[0])

    if casy[-1] != "23:55":
        casy.append("23:55")
        teploty.append(teploty[-1])

    data: dict[str, list] = {"Time": casy, "Temperature": teploty}

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Convert Time column to datetime
    df["Time"] = pd.to_datetime(df["Time"], format="%H:%M")

    # Sort DataFrame by Time
    df.sort_values("Time", inplace=True)

    # Set Time as index
    df.set_index("Time", inplace=True)

    # Resample the data to fill in missing time points
    df_resampled: pd.DataFrame = df.resample("5min").asfreq()

    # Interpolate missing values
    df_resampled["Temperature"] = df_resampled["Temperature"].interpolate()

    # Apply rolling average with a smaller window size and center=False
    df_smoothed: pd.DataFrame = df_resampled.rolling(window=3, center=False).mean()

    # Define custom colormap
    cmap_colors: list[tuple[float, str]] = [
        (0, "blue"),
        (0.2, "purple"),
        (0.7, "orange"),
        (1, "red"),
    ]
    custom_cmap: LinearSegmentedColormap = LinearSegmentedColormap.from_list(
        "custom_colormap", cmap_colors
    )

    # Normalize temperature values for color mapping
    norm = plt.Normalize(vmin=min, vmax=max)  # type: ignore
    filename_date, *rest = path.split("/")[-1].split(".")
    filename_room = rest[0] if rest else ""
    try:
        label: str = pd.to_datetime(filename_date).strftime("%d. %m. %Y")
    except (ValueError, pd.errors.ParserError):
        label = filename_date

    # Plotting with color based on Temperature values for smoothed data
    plt.figure(figsize=(10, 6))
    plt.scatter(
        df_smoothed.index,
        df_smoothed["Temperature"],
        c=df_smoothed["Temperature"],
        cmap=custom_cmap,
        norm=norm,
        label=label,
        marker="o",
    )  # type: ignore

    # Customize the plot
    plt.title(
        name
        + (f" v místnosti {filename_room.replace('_', ' ')}" if filename_room else "")
    )
    plt.xlabel("Time")
    plt.ylabel("Temperature (°C)")

    # Set fewer x-axis ticks for better readability
    plt.xticks(
        df_smoothed.index[::24], df_smoothed.index[::24].strftime("%H:%M"), rotation=45
    )  # type: ignore

    # Add colorbar
    cbar: Colorbar = plt.colorbar()
    cbar.set_label("Temperature (°C)")

    plt.legend()

    # Show the plot
    # plt.show()

    plt.savefig(f"{path}.png", dpi=171.5, bbox_inches="tight")
    plt.close("all")


if __name__ == "__main__":
    import os

    for file in os.listdir("WIP"):
        try:
            make_picture(f"WIP/{file}")
        except Exception as e:
            print(e)
