let errorClearTimeout;
let errorElement;

function showError(element, errorMessage) {
    if (errorElement) errorElement.remove();
    clearTimeout(errorClearTimeout);
    errorElement = document.createElement("div");
    errorElement.innerText = errorMessage;
    errorElement.className = "error"
    element.after(errorElement);
    errorClearTimeout = setTimeout(() => {
        errorElement.remove();
    }, 3000)
    return;
}

function checkErrors(element) {
    const configProfile = element.parentElement.parentElement;
    const nameInput = configProfile.firstElementChild;
    const configName = nameInput.nextElementSibling;
    const allNameElements = document.getElementsByClassName("config-name");
    for (let i = 0; i < allNameElements.length; i++) {
        if (allNameElements[i] !== configName) {
            if (allNameElements[i].innerText == nameInput.value) {
                showError(configProfile, "Name already exists");
                return true
            }
        };
    }
    if (nameInput.value == "") {
        showError(configProfile, "Name cannot be empty");
        return true
    }
    const configParams = configProfile.getElementsByClassName("config-param")
    for (let i = 0; i < configParams.length; i++) {
        let configValueInput = configParams[i].getElementsByClassName("config-value-input")[0];
        let value = configValueInput.value;
        let dataLabel = configValueInput.parentElement.previousElementSibling.innerText;
        if (value == "") {
            showError(configProfile, `${dataLabel} must not be empty`);
            return true
        } else if (isNaN(value)) {
            showError(configProfile, `${dataLabel} must be a number`);
            return true
        }
    }
    return false
}

// when delete pressed
async function deleteConfig(buttonElement) {
    const configProfile = buttonElement.parentElement.parentElement;
    const configName = configProfile.getElementsByClassName("config-name")[0].innerText;
    try {
        const response = await fetch("/delete", {
            method: "POST",
            body: JSON.stringify({"name": configName}),
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            const data = await response.json();
            showError(configProfile, data.error);
            return false
        };
    } catch (error) {
        showError(configProfile, "Error submitting data");
        return false
    }

    configProfile.remove();

    const options = document.getElementById("select-config").getElementsByTagName("option");
    for (let i = 0; i < options.length; i++) {
        if (options[i].value == configName) {
            options[i].remove();
            break;
        }
    }

    return true
}

// adds input fields when edit pressed
function editConfig(buttonElement) {
    const configProfile = buttonElement.parentElement.parentElement;
    const configValues = configProfile.getElementsByClassName("config-value");
    buttonElement.style.display = "none";
    buttonElement.nextElementSibling.style.display = "inline-block";

    // name input
    const nameInput = document.createElement("input");
    nameInput.className = "config-name-input";
    nameInput.setAttribute("required", "");
    const configName = configProfile.firstElementChild
    nameInput.value = configName.innerText;
    nameInput.setAttribute("old-name", configName.innerText);
    configName.style.display = "none";
    configProfile.insertBefore(nameInput, configProfile.firstElementChild);

    for (let i = 0; i < configValues.length; i++) {
        let configValue = configValues[i];
        let input = document.createElement("input");
        input.setAttribute("required", "");
        input.className = "config-value-input";
        input.value = configValue.innerText;
        configValue.parentElement.insertBefore(input, configValue);
        configValue.style.display = "none";
    }
}

// sends config data to server
async function sendConfigToServer(buttonElement) {
    let submitJson = {};
    const configProfile = buttonElement.parentElement.parentElement;
    const nameInput = configProfile.firstElementChild;
    const oldName = nameInput.getAttribute("old-name")
    submitJson["old_name"] = oldName == "" ? null : oldName;
    submitJson["name"] = nameInput.value;
    const configParams = configProfile.getElementsByClassName("config-param")

    for (let i = 0; i < configParams.length; i++) {
        let configValueInput = configParams[i].getElementsByClassName("config-value-input")[0];
        let dataName = configValueInput.parentElement.parentElement.getAttribute("name");
        let value = configValueInput.value;
        submitJson[dataName] = value;
    };

    try {
        const response = await fetch("/edit", {
            method: "POST",
            body: JSON.stringify(submitJson),
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            const data = await response.json();
            showError(configProfile, data.error);
            return false
        };
    } catch (error) {
        showError(configProfile, "Error submitting data");
        return false
    }

    return true
}

//  removes input fields when submit edit or submit new pressed
async function submitConfig(buttonElement) {
    if (!await sendConfigToServer(buttonElement)) return false;

    const configProfile = buttonElement.parentElement.parentElement;
    const nameInput = configProfile.firstElementChild;
    const oldName = nameInput.getAttribute("old-name")
    const configName = nameInput.nextElementSibling;
    const configParams = configProfile.getElementsByClassName("config-param")

    configName.innerText = nameInput.value.trim().toLowerCase();
    nameInput.remove();
    configName.style.display = "inline-block";

    const options = document.getElementById("select-config").getElementsByTagName("option");
    for (let i = 0; i < options.length; i++) {
        if (oldName == "") {
            const option = document.createElement("option");
            option.value = configName.innerText;
            option.innerText = configName.innerText;
            document.getElementById("select-config").appendChild(option);
            break;
        } else if (options[i].value == oldName) {
            options[i].value = configName.innerText;
            options[i].innerText = configName.innerText;
            break;
        }
    }
    for (let i = 0; i < configParams.length; i++) {
        let configValue = configParams[i].getElementsByClassName("config-value")[0];
        let configValueInput = configParams[i].getElementsByClassName("config-value-input")[0];
        configValue.style.display = "inline-block";

        let value = configValueInput.value;

        configValueInput.nextElementSibling.innerText = value;
        configValueInput.remove();
    };

    return true
}

// when submit edit pressed
async function submitEditConfig(buttonElement) {
    if (!await submitConfig(buttonElement)) return;

    // additional DOM changes
    buttonElement.style.display = "none";
    buttonElement.previousElementSibling.style.display = "inline-block";

}

const configTemplate = `
<div class="config-profile">
    <input class="config-name-input" old-name="">
    <span class="config-name" style="display: none;"></span>
    <span class="config-param" name="on_ec_level">
        <span class="config-value-name">Pump ON</span>
        <span><input class="config-value-input" required><span style="display: none;" class="config-value">0</span><span class="config-value-unit">mS/cm</span></span>
    </span>
    <span class="config-param" name="on_light_level">
        <span class="config-value-name">UV light ON</span>
        <span><input class="config-value-input" required><span style="display: none;" class="config-value">0</span><span class="config-value-unit">lux</span></span>
    </span>
    <span class="config-param" name="off_light_level">
        <span class="config-value-name">UV light OFF</span>
        <span><input class="config-value-input" required><span style="display: none;" class="config-value">0</span><span class="config-value-unit">lux</span></span>
    </span>
    <span class="config-param" name="temp_setpoint">
        <span class="config-value-name">Temp. setpoint</span>
        <span><input class="config-value-input" required><span style="display: none;" class="config-value">0</span><span class="config-value-unit">°C</span></span>
    </span>
    <span class="config-param" name="temp_max">
        <span class="config-value-name">Temp. warning</span>
        <span><input class="config-value-input" required><span style="display: none;" class="config-value">0</span><span class="config-value-unit">°C</span></span>
    </span>
    <span class="config-buttons">
        <button type="button" onclick="submitNewConfig(this)">Submit</button>
        <button type="button" onclick="cancelNewConfig(this)">Cancel</button>
    </span>
</div>
`

const configButtons = `
<button type="button" onclick="editConfig(this)">Edit</button>
<button style="display: none;" type="button" onclick="submitEditConfig(this)">Submit</button>
<button type="button" onclick="deleteConfig(this)">Delete</button>
`

// when create new pressed
function createConfig() {
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = configTemplate;

    document.getElementById("config-profiles").appendChild(tempContainer.firstElementChild);
}


// when submit new pressed
async function submitNewConfig(buttonElement) {
    if (!await submitConfig(buttonElement)) return;

    // additional DOM changes
    const tempContainer = document.createElement('div');
    tempContainer.innerHTML = configButtons;
    buttonElement.nextElementSibling.remove();
    buttonElement.parentElement.append(...tempContainer.children);
    buttonElement.remove();
}

// when cancel new pressed
function cancelNewConfig(buttonElement) {
    buttonElement.parentElement.parentElement.remove();
}