const BACKEND_URL = "http://127.0.0.1:5000";

let currentRows = [];
let mlResults = [];
let segmentChartInstance = null;
let churnChartInstance = null;

document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTS
    // =========================================================

    const csvFile = document.getElementById("csvFile");
    const uploadButton = document.getElementById("uploadButton");
    const uploadStatus = document.getElementById("uploadStatus");
    const analysisLoading = document.getElementById("analysisLoading");
    const datasetSummary = document.getElementById("datasetSummary");

    // =========================================================
    // CSV PARSER
    // =========================================================

    function parseCSV(text) {
        const lines = text
            .split(/\r?\n/)
            .map(line => line.trim())
            .filter(line => line.length > 0);

        if (lines.length < 2) {
            return [];
        }

        const headers = lines[0]
            .split(",")
            .map(header => header.trim());

        return lines.slice(1).map(line => {
            const values = line.split(",");

            const row = {};

            headers.forEach((header, index) => {
                row[header] = values[index]
                    ? values[index].trim()
                    : "";
            });

            return row;
        });
    }

    // =========================================================
    // HELPERS
    // =========================================================

    function getUniqueCustomerIds(rows) {
        return [
            ...new Set(
                rows
                    .map(row => row.customer_id)
                    .filter(id => id !== undefined && id !== "")
            )
        ];
    }

    function getValidMLResults() {
        return mlResults.filter(
            item =>
                item &&
                item.success &&
                item.result &&
                item.result.customer_profile
        );
    }

    function showAnalytics() {
        const elements = document.querySelectorAll(".analytics-hidden");

        elements.forEach(element => {
            element.classList.remove("analytics-hidden");
        });

        const emptyStates = document.querySelectorAll(".empty-state");

        emptyStates.forEach(element => {
            element.style.display = "none";
        });
    }

    // =========================================================
    // DASHBOARD
    // =========================================================

    function updateDashboard(rows, results) {

        const totalCustomersElement =
            document.getElementById("totalCustomers");

        const totalTransactionsElement =
            document.getElementById("totalTransactions");

        const totalRevenueElement =
            document.getElementById("totalRevenue");

        const atRiskCustomersElement =
            document.getElementById("atRiskCustomers");

        const customerIds = getUniqueCustomerIds(rows);

        const totalCustomers = customerIds.length;

        const totalTransactions = rows.length;

        const totalRevenue = rows.reduce((total, row) => {
            const amount = parseFloat(row.amount);
            return total + (isNaN(amount) ? 0 : amount);
        }, 0);

        const validResults = results.filter(
            item =>
                item &&
                item.success &&
                item.result &&
                item.result.customer_profile
        );

        const atRiskCustomers = validResults.filter(item => {

            const risk =
                item.result.customer_profile.risk_level;

            return risk === "High" || risk === "Medium";

        }).length;

        if (totalCustomersElement) {
            totalCustomersElement.textContent = totalCustomers;
        }

        if (totalTransactionsElement) {
            totalTransactionsElement.textContent = totalTransactions;
        }

        if (totalRevenueElement) {
            totalRevenueElement.textContent =
                "₹" +
                totalRevenue.toLocaleString("en-IN", {
                    maximumFractionDigits: 2
                });
        }

        if (atRiskCustomersElement) {
            atRiskCustomersElement.textContent = atRiskCustomers;
        }
    }

    // =========================================================
    // CUSTOMER TABLE
    // =========================================================

    function updateCustomerTable(rows) {

        const tableBody =
            document.getElementById("customerTableBody");

        if (!tableBody) {
            return;
        }

        tableBody.innerHTML = "";

        const displayRows = rows.slice(0, 100);

        displayRows.forEach(row => {

            const tr = document.createElement("tr");

            const customerCell =
                document.createElement("td");

            const dateCell =
                document.createElement("td");

            const amountCell =
                document.createElement("td");

            customerCell.textContent =
                row.customer_id || "-";

            dateCell.textContent =
                row.purchase_date || "-";

            const amount =
                parseFloat(row.amount);

            amountCell.textContent =
                "₹" +
                (
                    isNaN(amount)
                        ? 0
                        : amount
                ).toLocaleString("en-IN", {
                    maximumFractionDigits: 2
                });

            tr.appendChild(customerCell);
            tr.appendChild(dateCell);
            tr.appendChild(amountCell);

            tableBody.appendChild(tr);
        });
    }

    // =========================================================
    // SEGMENTATION
    // =========================================================

    function calculateMLSegmentation(results) {

        const segments = {
            "Active / Regular": 0,
            "Inactive / At Risk": 0,
            "VIP / High Value": 0
        };

        results.forEach(customer => {

            if (
                !customer ||
                !customer.success ||
                !customer.result ||
                !customer.result.customer_profile
            ) {
                return;
            }

            const segment =
                customer.result.customer_profile.segment;

            if (
                Object.prototype.hasOwnProperty.call(
                    segments,
                    segment
                )
            ) {
                segments[segment]++;
            }
        });

        return segments;
    }

    function updateSegmentationCards(segmentCounts) {

        const cards =
            document.querySelectorAll(".segment-card");

        cards.forEach(card => {

            const heading =
                card.querySelector("h3");

            const paragraph =
                card.querySelector("p");

            if (!heading || !paragraph) {
                return;
            }

            const title =
                heading.textContent.trim();

            let count = 0;

            if (title === "Active / Regular") {
                count = segmentCounts["Active / Regular"];
            }

            if (title === "Inactive / At Risk") {
                count = segmentCounts["Inactive / At Risk"];
            }

            if (title === "VIP / High Value") {
                count = segmentCounts["VIP / High Value"];
            }

            paragraph.textContent =
                `${count} Customers`;
        });
    }

    function updateSegmentationChart(segmentCounts) {

        const canvas =
            document.getElementById("segmentChart");

        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        if (segmentChartInstance) {
            segmentChartInstance.destroy();
        }

        segmentChartInstance = new Chart(
            canvas,
            {
                type: "doughnut",

                data: {
                    labels: [
                        "Active / Regular",
                        "Inactive / At Risk",
                        "VIP / High Value"
                    ],

                    datasets: [
                        {
                            data: [
                                segmentCounts["Active / Regular"],
                                segmentCounts["Inactive / At Risk"],
                                segmentCounts["VIP / High Value"]
                            ]
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            }
        );
    }

    // =========================================================
    // CHURN
    // =========================================================

    function calculateMLChurn(results) {

        const churn = {
            "High Risk": 0,
            "Medium Risk": 0,
            "Low Risk": 0
        };

        results.forEach(customer => {

            if (
                !customer ||
                !customer.success ||
                !customer.result ||
                !customer.result.customer_profile
            ) {
                return;
            }

            const risk =
                customer.result.customer_profile.risk_level;

            if (
                Object.prototype.hasOwnProperty.call(
                    churn,
                    risk + " Risk"
                )
            ) {
                churn[risk + " Risk"]++;
            }
        });

        return churn;
    }

    function updateChurnCards(churnCounts) {

        const cards =
            document.querySelectorAll(".churn-card");

        cards.forEach(card => {

            const heading =
                card.querySelector("h3");

            const number =
                card.querySelector(".churn-number");

            if (!heading || !number) {
                return;
            }

            const title =
                heading.textContent.trim();

            if (
                Object.prototype.hasOwnProperty.call(
                    churnCounts,
                    title
                )
            ) {
                number.textContent =
                    churnCounts[title];
            }
        });
    }

    function updateChurnChart(churnCounts) {

        const canvas =
            document.getElementById("churnChart");

        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        if (churnChartInstance) {
            churnChartInstance.destroy();
        }

        churnChartInstance = new Chart(
            canvas,
            {
                type: "bar",

                data: {
                    labels: [
                        "High Risk",
                        "Medium Risk",
                        "Low Risk"
                    ],

                    datasets: [
                        {
                            label: "Customers",

                            data: [
                                churnCounts["High Risk"],
                                churnCounts["Medium Risk"],
                                churnCounts["Low Risk"]
                            ]
                        }
                    ]
                },

                options: {
                    responsive: true,
                    maintainAspectRatio: false,

                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    },

                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            }
        );
    }

    // =========================================================
    // NEXT BEST ACTION
    // =========================================================

    function priorityValue(priority) {

        if (priority === "High") {
            return 3;
        }

        if (priority === "Medium") {
            return 2;
        }

        return 1;
    }

    function updateNextBestAction(results) {

        const nbaContent =
            document.getElementById("nbaContent");

        if (!nbaContent) {
            return;
        }

        nbaContent.innerHTML = "";

        const validResults =
            getValidMLResults()
                .slice()
                .sort((a, b) => {

                    const priorityA =
                        a.result.next_best_action
                            ? a.result.next_best_action.priority
                            : "Low";

                    const priorityB =
                        b.result.next_best_action
                            ? b.result.next_best_action.priority
                            : "Low";

                    return (
                        priorityValue(priorityB) -
                        priorityValue(priorityA)
                    );
                });

        const displayResults =
            validResults.slice(0, 6);

        if (displayResults.length === 0) {

            nbaContent.innerHTML =
                "<p>No recommendations available.</p>";

            return;
        }

        displayResults.forEach(customer => {

            const profile =
                customer.result.customer_profile;

            const action =
                customer.result.next_best_action || {};

            const card =
                document.createElement("div");

            card.className = "nba-card";

            const customerId =
                customer.customer_id || "Unknown";

            const probability =
                profile.churn_probability !== undefined
                    ? (
                        Number(
                            profile.churn_probability
                        ) * 100
                    ).toFixed(1)
                    : "0.0";

            card.innerHTML = `
                <h3>${customerId}</h3>

                <p>
                    <strong>Action:</strong>
                    ${action.action || "No Action"}
                </p>

                <p>
                    <strong>Priority:</strong>
                    ${action.priority || "Low"}
                </p>

                <p>
                    <strong>Churn Risk:</strong>
                    ${profile.risk_level || "Low"}
                </p>

                <p>
                    <strong>Churn Probability:</strong>
                    ${probability}%
                </p>

                <p>
                    <strong>Reason:</strong>
                    ${
                        action.reason ||
                        "No configured NBA rule matched this customer."
                    }
                </p>
            `;

            nbaContent.appendChild(card);
        });
    }

    // =========================================================
    // BUSINESS INSIGHTS
    // =========================================================

    function updateBusinessInsights(
        segmentCounts,
        churnCounts,
        results
    ) {

        const insightsContent =
            document.getElementById("insightsContent");

        if (!insightsContent) {
            return;
        }

        const cards =
            insightsContent.querySelectorAll(
                ".insight-card"
            );

        if (cards.length < 3) {
            return;
        }

        // -----------------------------------------
        // Churn insight
        // -----------------------------------------

        const totalCustomers =
            Object.values(churnCounts)
                .reduce(
                    (sum, value) => sum + value,
                    0
                );

        const highRisk =
            churnCounts["High Risk"];

        const mediumRisk =
            churnCounts["Medium Risk"];

        const atRisk =
            highRisk + mediumRisk;

        let churnText =
            "No churn risk data available.";

        if (totalCustomers > 0) {

            const percentage =
                (
                    atRisk /
                    totalCustomers *
                    100
                ).toFixed(1);

            churnText =
                `${atRisk} of ${totalCustomers} customers `
                + `are in High or Medium churn risk `
                + `(${percentage}%).`;
        }

        cards[0].querySelector("p").textContent =
            churnText;

        // -----------------------------------------
        // Largest segment
        // -----------------------------------------

        let largestSegment =
            "No segment data available.";

        const entries =
            Object.entries(segmentCounts);

        if (entries.length > 0) {

            const largest =
                entries.reduce(
                    (max, current) =>
                        current[1] > max[1]
                            ? current
                            : max
                );

            largestSegment =
                `${largest[0]} is the largest segment `
                + `with ${largest[1]} customers.`;
        }

        cards[1].querySelector("p").textContent =
            largestSegment;

        // -----------------------------------------
        // Recommended focus
        // -----------------------------------------

        const highPriorityActions =
            results.filter(customer => {

                if (
                    !customer ||
                    !customer.success ||
                    !customer.result
                ) {
                    return false;
                }

                const action =
                    customer.result.next_best_action;

                return (
                    action &&
                    action.priority === "High"
                );
            });

        let focusText =
            "No high-priority action is currently identified.";

        if (highPriorityActions.length > 0) {

            const firstAction =
                highPriorityActions[0]
                    .result
                    .next_best_action;

            focusText =
                `${highPriorityActions.length} customers `
                + `have a High priority recommendation. `
                + `Example action: `
                + `${firstAction.action || "No Action"}.`;
        }

        cards[2].querySelector("p").textContent =
            focusText;
    }

    // =========================================================
    // DATASET SUMMARY
    // =========================================================

    function updateDatasetSummary(
        rows,
        customerIds,
        datasetId
    ) {

        if (!datasetSummary) {
            return;
        }

        datasetSummary.innerHTML = `
            <p>
                <strong>Dataset ID:</strong>
                ${datasetId}
            </p>

            <p>
                <strong>Total Customers:</strong>
                ${customerIds.length}
            </p>

            <p>
                <strong>Total Transactions:</strong>
                ${rows.length}
            </p>
        `;
    }

    // =========================================================
    // MAIN ANALYSIS
    // =========================================================

    async function analyzeDataset(
        selectedFile
    ) {

        // -----------------------------------------
        // Read CSV
        // -----------------------------------------

        const csvText =
            await selectedFile.text();

        const rows =
            parseCSV(csvText);

        if (rows.length === 0) {
            throw new Error(
                "CSV file is empty or invalid."
            );
        }

        // -----------------------------------------
        // Validate ML columns
        // -----------------------------------------

        const requiredColumns = [
            "customer_id",
            "invoice",
            "purchase_date",
            "quantity",
            "amount"
        ];

        const headers =
            Object.keys(rows[0]);

        const missingColumns =
            requiredColumns.filter(
                column =>
                    !headers.includes(column)
            );

        if (missingColumns.length > 0) {

            throw new Error(
                "CSV is missing required ML columns: "
                + missingColumns.join(", ")
            );
        }

        currentRows = rows;

        // -----------------------------------------
        // Upload to backend
        // -----------------------------------------

        uploadStatus.textContent =
            "Uploading dataset to backend...";

        uploadStatus.className =
            "status-info";

        const formData =
            new FormData();

        formData.append(
            "file",
            selectedFile
        );

        const uploadResponse =
            await fetch(
                `${BACKEND_URL}/api/datasets/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );

        const uploadData =
            await uploadResponse.json();

        if (
            !uploadResponse.ok ||
            !uploadData.success
        ) {
            throw new Error(
                uploadData.message ||
                "Dataset upload failed."
            );
        }

        const datasetId =
            uploadData.dataset_id;

        console.log(
            "Backend upload successful:",
            uploadData
        );

        // -----------------------------------------
        // Get customers
        // -----------------------------------------

        const customerIds =
            getUniqueCustomerIds(rows);

        console.log(
            "Customers found:",
            customerIds
        );

        if (customerIds.length === 0) {
            throw new Error(
                "No customer IDs found in CSV."
            );
        }

        uploadStatus.textContent =
            `Running ML analysis for ${customerIds.length} customers...`;

        // -----------------------------------------
        // Call ML backend for every customer
        // -----------------------------------------

        const results =
            await Promise.all(
                customerIds.map(
                    async customerId => {

                        try {

                            const response =
                                await fetch(
                                    `${BACKEND_URL}/api/ml/dataset/${datasetId}/customer/${encodeURIComponent(customerId)}`
                                );

                            const result =
                                await response.json();

                            return result;

                        } catch (error) {

                            console.error(
                                `ML error for ${customerId}:`,
                                error
                            );

                            return {
                                success: false,
                                customer_id: customerId,
                                message: error.message
                            };
                        }
                    }
                )
            );

        mlResults = results;

        console.log(
            "All ML Results:",
            mlResults
        );

        // -----------------------------------------
        // Update Dashboard
        // -----------------------------------------

        updateDashboard(
            rows,
            mlResults
        );

        updateCustomerTable(
            rows
        );

        updateDatasetSummary(
            rows,
            customerIds,
            datasetId
        );

        // -----------------------------------------
        // Segmentation
        // -----------------------------------------

        const segmentCounts =
            calculateMLSegmentation(
                mlResults
            );

        updateSegmentationCards(
            segmentCounts
        );

        updateSegmentationChart(
            segmentCounts
        );

        // -----------------------------------------
        // Churn
        // -----------------------------------------

        const churnCounts =
            calculateMLChurn(
                mlResults
            );

        updateChurnCards(
            churnCounts
        );

        updateChurnChart(
            churnCounts
        );

        // -----------------------------------------
        // NBA
        // -----------------------------------------

        updateNextBestAction(
            mlResults
        );

        // -----------------------------------------
        // Business Insights
        // -----------------------------------------

        updateBusinessInsights(
            segmentCounts,
            churnCounts,
            mlResults
        );

        // -----------------------------------------
        // Show analytics
        // -----------------------------------------

        showAnalytics();

        uploadStatus.textContent =
            "Dataset analyzed successfully.";

        uploadStatus.className =
            "status-success";

        console.log(
            "Dataset ID:",
            datasetId
        );

        console.log(
            "Final ML Results:",
            mlResults
        );
    }

    // =========================================================
    // UPLOAD BUTTON
    // =========================================================

    if (uploadButton) {

        uploadButton.addEventListener(
            "click",
            async function () {

                if (!csvFile.files.length) {

                    uploadStatus.textContent =
                        "Please select a CSV file first.";

                    uploadStatus.className =
                        "status-error";

                    return;
                }

                const selectedFile =
                    csvFile.files[0];

                // -----------------------------------------
                // File type check
                // -----------------------------------------

                if (
                    !selectedFile.name
                        .toLowerCase()
                        .endsWith(".csv")
                ) {

                    uploadStatus.textContent =
                        "Please select a CSV file.";

                    uploadStatus.className =
                        "status-error";

                    return;
                }

                try {

                    if (analysisLoading) {
                        analysisLoading.classList.add(
                            "show"
                        );
                    }

                    uploadButton.disabled = true;

                    await analyzeDataset(
                        selectedFile
                    );

                } catch (error) {

                    console.error(
                        "Dataset analysis error:",
                        error
                    );

                    uploadStatus.textContent =
                        error.message ||
                        "Unable to analyze dataset.";

                    uploadStatus.className =
                        "status-error";

                } finally {

                    uploadButton.disabled = false;

                    if (analysisLoading) {
                        analysisLoading.classList.remove(
                            "show"
                        );
                    }
                }
            }
        );
    }

});