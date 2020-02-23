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
    var secondTable = document.querySelectorAll("#listTableLinkBody")[1]
    const descriptions = [...secondTable.querySelectorAll(".table_column_2 .changeText")].map(e => e.innerText.trim().replace(/,/g, ' '));
    const dates = [...secondTable.querySelectorAll(".table_column_0")].map(e => e.innerText.trim());
    const debits = [...secondTable.querySelectorAll(".table_column_4")].map(e => {
        var match = e.innerText.match(/\d+\.\d\d/);
        if (match == null) return "";
        return match[0].trim();
    });

    const credits = [...secondTable.querySelectorAll(".table_column_5")].map(e => {
        var match = e.innerText.match(/\d+\.\d\d/);
        if (match == null) return "";
        return match[0].trim();
    });

    if (descriptions.length != dates.length || descriptions.length != credits.length || descriptions.length != debits.length) {

        alert("uneven numbers of rows in each column problem.");
        console.error(descriptions.length, dates.length, debits.length, credits.length);
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
        let credit = credits[i];
        let debit = debits[i];
        console.log(`"${credit}" "${debit}"`);
        var amount;
        if (credit.trim() == "") {
            amount = `-${debit}`;
        } else {
            amount = credit;
        }
        appendCsv(dates[i], descriptions[i], amount);
    }

    if (lastPage) {
        const url = makeTextFile(csv);

        window.open(url, "_blank");
    }
}
