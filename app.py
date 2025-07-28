from quart import Quart, request, jsonify, render_template
from smartbindb import SmartBinDB

# Quart অ্যাপ তৈরি
app = Quart(__name__)

# SmartBinDB ক্লাস ইন্সট্যান্স তৈরি
smartdb = SmartBinDB()

# ইনডেক্স পেইজ (Documentation) এর জন্য রুট
@app.route("/", methods=["GET"])
async def index():
    return await render_template("index.html")

# BIN তথ্য অনুসন্ধান API Endpoint
@app.route("/api/bin", methods=["GET"])
async def get_bin_info():
    bin_number = request.args.get("bin")
    if not bin_number:
        return jsonify({"error": "bin parameter is required"}), 400

    result = await smartdb.get_bin_info(bin_number)

    if result.get("status") != "SUCCESS":
        return jsonify({"error": "BIN not found"}), 404

    return jsonify(result.get("data"))

# কান্ট্রি ভিত্তিক BIN অনুসন্ধান API Endpoint (রিসোর্স লিমিট দিয়ে)
@app.route("/api/country", methods=["GET"])
async def get_bins_by_country():
    if request.args.get("list"):
        # Hardcoded country list as a temporary fix
        countries = [
            {"code": "US", "name": "United States"},
            {"code": "GB", "name": "United Kingdom"},
            {"code": "CA", "name": "Canada"},
            {"code": "AU", "name": "Australia"},
            {"code": "DE", "name": "Germany"},
            {"code": "FR", "name": "France"},
            {"code": "JP", "name": "Japan"},
        ]
        return jsonify(countries)

    country_code = request.args.get("country")
    if not country_code:
        return jsonify({"error": "country parameter is required"}), 400

    limit = request.args.get("limit", 10, type=int)

    result = await smartdb.get_bins_by_country(country_code, limit)

    if result.get("status") != "SUCCESS":
        return jsonify({"error": "No BINs found for the country"}), 404

    # Add meta object to the response
    response_data = {
        "data": result.get("data"),
        "meta": {
            "returned": len(result.get("data", [])),
            "total": result.get("total_bins", len(result.get("data", [])))
        }
    }
    return jsonify(response_data)

# This block is for local development only and should not be part of the Vercel deployment.
# Vercel uses its own server to run the Quart app.
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
