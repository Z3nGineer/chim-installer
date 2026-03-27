local function getRootDirectory()
    local str = debug.getinfo(2, "S").source:sub(2)
    return str:match("(.*[/\\])") or ""
end

function writeIniFile(data)
    local root = getRootDirectory()
    local file = io.open(root .. "config.ini", "w")
    if not file then
        error("Could not open file config.ini")
    end

    for section, values in pairs(data) do
        file:write("[" .. section .. "]\n")
        for key, value in pairs(values) do
            file:write(key .. " = " .. serialize(value) .. "\n")
        end
        file:write("\n")
    end

    file:close()
end

function readIniFile()
    local root = getRootDirectory()
    local file = io.open(root .. "config.ini", "r")
    if not file then
        error("Could not open file config.ini")
    end

    local data = {}
    local currentSection = nil

    for line in file:lines() do
        local section = line:match("^%[([^%]]+)%]$")
        if section then
            currentSection = section
            data[currentSection] = {}
        else
            local key, value = line:match("^([^=]+) = ([^=]+)$")
            if key and value and currentSection then
                data[currentSection][key] = deserialize(value)
            end
        end
    end

    file:close()
    return data
end

function serialize(value)
    if type(value) == "boolean" then
        if value == true then
            return "True"
        end

        return "False"
    end

    return value
end

function deserialize(value)
    if value:lower() == "true" then
        return true
    end

    if value:lower() == "false" then
        return false
    end

    return value
end

return {
    writeIniFile = writeIniFile,
    readIniFile = readIniFile
}