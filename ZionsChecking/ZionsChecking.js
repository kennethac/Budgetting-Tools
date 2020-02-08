var csv = "";

async function pause(milli) {
    return new Promise((finish) => {
        setTimeout(finish, milli);
    });
}

function resetCsv() {
    csv = "";
}

async function getCSVForPage(lastPage = false) {
    // Expand all the "more" boxes
    [...document.querySelectorAll("small")].filter(e => e.innerText == 'More').forEach(e => e.click())
    await pause(500);
    const descriptions = [...document.querySelectorAll(".table_column_2")].map(e => e.innerText);
    const dates = [...document.querySelectorAll(".table_column_0")].map(e => e.innerText);
    const amounts = [...document.querySelectorAll(".table_column_4")].map(e => {
        var match = e.innerText.match(/\d+\.\d\d/);
        if (match == null) return "";
        return match[0];
    });

    if (descriptions.length != dates.length || descriptions.length != amounts.length) {

        alert("uneven numbers of rows in each column problem.");
        console.error(descriptions.length, dates.length, amounts.length);
        return;
    }

    function appendCsv(date, description, amount) {
        csv += "Zions Debit," + date.toString() + "," + date.toString() + ",," + description + "," + amount + "\n";
    }

    var textFile;

    function makeTextFile(text) {
        var data = new Blob([text], { type: 'text/plain' });

        // If we are replacing a previously generated file we need to
        // manually revoke the object URL to avoid memory leaks.
        if (textFile !== null) {
            window.URL.revokeObjectURL(textFile);
        }

        textFile = window.URL.createObjectURL(data);

        return textFile;
    };

    for (var i = 0; i < descriptions.length; i++) {
        appendCsv(dates[i], descriptions[i], amounts[i]);
    }

    if (lastPage) {
        const url = makeTextFile(csv);

        window.open(url, "_blank");
    }
}
