# Sarvatobhadra Chakra — Streamlit

Historical Sarvatobhadra Chakra workbench using Swiss Ephemeris and Lahiri sidereal calculations.

## Features
- 9x9 / 81-cell Sarvatobhadra Chakra
- 28 nakshatras including Abhijit
- 12 rashis, 20 consonant cells, 16 vowel corners, five tithi families
- Natal Panchaka reference: Moon nakshatra, Moon sign, tithi family, weekday, optional name sound
- Historical transit date/time replay
- Planetary sidereal longitude, rashi, nakshatra, pada, speed and retrograde status
- Motion-based Vedha selection
- Benefic/malefic Vedha hit table
- Historical daily replay with CSV download
- No API key required

## Streamlit Community Cloud
1. Create a GitHub repository and upload these files.
2. Go to Streamlit Community Cloud and choose **Create app**.
3. Select your repository, branch and `app.py`.
4. Deploy.

Streamlit Community Cloud installs Python dependencies from `requirements.txt`.

## Important methodological note
Sarvatobhadra Chakra has source/lineage variations, especially around weekday placement and the direction selected for Vedha under planetary motion. This app uses a documented motion-based convention and keeps the calculation deterministic. It is an analytical astrology tool, not a scientifically validated forecasting model.


## Streamlit Community Cloud deployment

Use Python 3.12 in Streamlit Community Cloud Advanced settings. The astronomy dependency is `pysweph==2.10.3.5`; it keeps the existing `import swisseph as swe` API used by the app.

1. Create a GitHub repository.
2. Put `app.py` and `requirements.txt` in the repository root.
3. In Streamlit Community Cloud choose **Create app** and select `app.py`.
4. In **Advanced settings**, select **Python 3.12**.
5. Deploy.

Do not use `pyswisseph==2.10.3.5`: that package/version combination is not available on PyPI.
