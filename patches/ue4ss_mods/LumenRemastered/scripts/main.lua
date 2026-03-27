UEHelpers = require('UEHelpers')
local ConfigHelper = require('ConfigHelper')
engine = FindFirstOf('Engine')
menu = FindFirstOf('VPlayerMenuViewModel')
ksl = UEHelpers.GetKismetSystemLibrary()

-- Patched: wrap ExecuteConsoleCommand to pass 4 args (UE4SS API change)
local _origExecCmd = ksl.ExecuteConsoleCommand
ksl.ExecuteConsoleCommand = function(self, eng, cmd, thirdArg, ...)
    local pc = UEHelpers.GetPlayerController() or thirdArg
    return _origExecCmd(self, eng, cmd, pc, false)
end

local config = ConfigHelper.readIniFile()
local hudVisible = true

NotifyOnNewObject("/Script/Altar.AltarCommonGameViewportClient", function(viewPort)
    SetGlobalSettings()
    SetSkylightIntensity()

    RegisterHook("/Script/Altar.VPlayerMenuViewModel:SetCurrentPage", function(context)
        SetSkylightIntensity()

        local PostProcessingVolumes = FindAllOf("PostProcessVolume")
        if PostProcessingVolumes ~= nil then
            for _, object in ipairs(PostProcessingVolumes) do
                SetExteriorWhiteBalance(object)
            end
        end

        local PostProcessComponents = FindAllOf("PostProcessComponent")
        if PostProcessComponents ~= nil then
            for _, object in ipairs(PostProcessComponents) do
                SetInteriorWhiteBalance(object)
            end
        end
    end)
end)

NotifyOnNewObject("/Script/Engine.PostProcessVolume", function(object)
    ExecuteWithDelay(10, function()
        SetExteriorSettings(object)
        SetColorCorrection(object)
        SetExteriorWhiteBalance(object)
    end)
end)

NotifyOnNewObject("/Script/Engine.PostProcessComponent", function(object)
    ExecuteWithDelay(10, function()
        SetInteriorSettings(object)
        SetColorCorrection(object)
        SetInteriorWhiteBalance(object)
    end)
end)

NotifyOnNewObject("/Script/Engine.SkyAtmosphereComponent", function(object)
    ExecuteWithDelay(10, function()
        SetSkyAtmosphereSettings(object)
    end)
end)

RegisterKeyBind(Key.END, { ModifierKey.ALT }, function()
    local uiSystem = FindFirstOf("VAltarUISubsystem")
    if not uiSystem:IsValid() then
        print("[LumenRemastered] AltarUISubsystem not found")
        return
    end

    hudVisible = not hudVisible
    uiSystem:ToggleHUDVisibility(hudVisible)
end)

RegisterKeyBind(Key.DEL, { ModifierKey.ALT }, function()
    config["General"].Enabled = not config["General"].Enabled
    ConfigHelper.writeIniFile(config)

    SetGlobalSettings()
    SetSkylightIntensity()

    local PostProcessingVolumes = FindAllOf("PostProcessVolume")
    if PostProcessingVolumes ~= nil then
        for _, object in ipairs(PostProcessingVolumes) do
            SetExteriorSettings(object)
            SetColorCorrection(object)
            SetExteriorWhiteBalance(object)
        end
    end

    local PostProcessComponents = FindAllOf("PostProcessComponent")
    if PostProcessComponents ~= nil then
        for _, object in ipairs(PostProcessComponents) do
            SetInteriorSettings(object)
            SetColorCorrection(object)
            SetInteriorWhiteBalance(object)
        end
    end

    local SkyAtmosphereComponents = FindAllOf("SkyAtmosphereComponent")
    if SkyAtmosphereComponents ~= nil then
        for _, object in ipairs(SkyAtmosphereComponents) do
            SetSkyAtmosphereSettings(object)
        end
    end
end)

RegisterKeyBind(Key.INS, { ModifierKey.ALT }, function()
    config["ColorCorrection"].Enabled = not config["ColorCorrection"].Enabled
    ConfigHelper.writeIniFile(config)

    local PostProcessingVolumes = FindAllOf("PostProcessVolume")
    if PostProcessingVolumes ~= nil then
        for _, object in ipairs(PostProcessingVolumes) do
            SetColorCorrection(object)
            SetExteriorWhiteBalance(object)
        end
    end

    local PostProcessComponents = FindAllOf("PostProcessComponent")
    if PostProcessComponents ~= nil then
        for _, object in ipairs(PostProcessComponents) do
            SetColorCorrection(object)
            SetInteriorWhiteBalance(object)
        end
    end
end)

RegisterKeyBind(Key.PAGE_DOWN, { ModifierKey.ALT }, function()
    if IsOutside() then
        config["AutoExposure"].ExteriorBias = config["AutoExposure"].ExteriorBias - 0.2
        config["AutoExposure"].ExteriorShadowContrast = config["AutoExposure"].ExteriorShadowContrast + 0.02
    elseif IsInDungeon() then
        config["AutoExposure"].DungeonOffset = config["AutoExposure"].DungeonOffset - 0.2
    else
        config["AutoExposure"].InteriorBias = config["AutoExposure"].InteriorBias - 0.2
        config["AutoExposure"].InteriorShadowContrast = config["AutoExposure"].InteriorShadowContrast + 0.02
    end

    ConfigHelper.writeIniFile(config)

    UpdateInteriorAndExteriorSettings()
end)

RegisterKeyBind(Key.PAGE_UP, { ModifierKey.ALT }, function()
    if IsOutside() then
        config["AutoExposure"].ExteriorBias = config["AutoExposure"].ExteriorBias + 0.2
        config["AutoExposure"].ExteriorShadowContrast = config["AutoExposure"].ExteriorShadowContrast - 0.02
    elseif IsInDungeon() then
        config["AutoExposure"].DungeonOffset = config["AutoExposure"].DungeonOffset + 0.2
    else
        config["AutoExposure"].InteriorBias = config["AutoExposure"].InteriorBias + 0.2
        config["AutoExposure"].InteriorShadowContrast = config["AutoExposure"].InteriorShadowContrast - 0.02
    end

    ConfigHelper.writeIniFile(config)

    UpdateInteriorAndExteriorSettings()
end)

function IsOutside()
    local PostProcessingVolumes = FindFirstOf("PostProcessVolume")
    if PostProcessingVolumes ~= nil then
        return PostProcessingVolumes:IsValid()
    end

    return false
end

function IsInDungeon()
    local PostProcessComponents = FindAllOf("PostProcessComponent")
    if PostProcessComponents ~= nil then
        for _, object in ipairs(PostProcessComponents) do
            local environmentName = object:GetFullName()
            if string.find(environmentName, "Crypt") or
                    string.find(environmentName, "Mine") or
                    string.find(environmentName, "Cave") or
                    string.find(environmentName, "Ruin") or
                    string.find(environmentName, "Temple")
            then
                return true
            end
        end
    end

    return false
end

function UpdateInteriorAndExteriorSettings()
    local PostProcessingVolumes = FindAllOf("PostProcessVolume")
    if PostProcessingVolumes ~= nil then
        for _, object in ipairs(PostProcessingVolumes) do
            SetExteriorSettings(object)
        end
    end

    local PostProcessComponents = FindAllOf("PostProcessComponent")
    if PostProcessComponents ~= nil then
        for _, object in ipairs(PostProcessComponents) do
            SetInteriorSettings(object)
        end
    end
end

function SetGlobalSettings()
    if (config["General"].Enabled == false) then
        ResetGlobalSettings()
        return
    end

    ExecuteInGameThread(function()
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.LensAttenuation 0.86", nil)
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.ExponentialTransitionDistance 4.2", nil)
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.MethodOverride 2", nil)
        ksl:ExecuteConsoleCommand(engine, "r.VolumetricFog.Emissive 0", nil)
        ksl:ExecuteConsoleCommand(engine, "r.Lumen.SampleFog 1", nil)
    end)

    ExecuteWithDelay(1, function()
        ExecuteInGameThread(function()
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.LensAttenuation 0.86", nil)
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.ExponentialTransitionDistance 4.2", nil)
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.MethodOverride 2", nil)
            ksl:ExecuteConsoleCommand(engine, "r.VolumetricFog.Emissive 0", nil)
            ksl:ExecuteConsoleCommand(engine, "r.Lumen.SampleFog 1", nil)
        end)
    end)
end

function ResetGlobalSettings()
    ExecuteInGameThread(function()
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.LensAttenuation 0.78", nil)
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.ExponentialTransitionDistance 1.5", nil)
        ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.MethodOverride -1", nil)
        ksl:ExecuteConsoleCommand(engine, "r.VolumetricFog.Emissive 1", nil)
        ksl:ExecuteConsoleCommand(engine, "r.Lumen.SampleFog 0", nil)
    end)

    ExecuteWithDelay(1, function()
        ExecuteInGameThread(function()
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.LensAttenuation 0.78", nil)
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.ExponentialTransitionDistance 1.5", nil)
            ksl:ExecuteConsoleCommand(engine, "r.EyeAdaptation.MethodOverride -1", nil)
            ksl:ExecuteConsoleCommand(engine, "r.VolumetricFog.Emissive 1", nil)
            ksl:ExecuteConsoleCommand(engine, "r.Lumen.SampleFog 0", nil)
        end)
    end)
end

function SetExteriorSettings(object)
    if (config["General"].Enabled == false) then
        ResetExteriorSettings(object)
        return
    end

    local exposureBias = config["AutoExposure"].ExteriorBias
    local shadowContrast = config["AutoExposure"].ExteriorShadowContrast

    object.Settings.bOverride_LumenSkylightLeaking = false

    object.Settings.bOverride_LumenDiffuseColorBoost = true
    object.Settings.LumenDiffuseColorBoost = 1.2

    object.Settings.AmbientOcclusionIntensity = 0.66
    object.Settings.AmbientOcclusionRadius = 120.0
    object.Settings.AmbientOcclusionPower = 3.8

    object.Settings.bOverride_BloomIntensity = true
    object.Settings.BloomIntensity = config["General"].BloomIntensity

    object.Settings.bOverride_LumenReflectionMaxRoughnessToTrace = true
    object.Settings.LumenReflectionMaxRoughnessToTrace = config["General"].ReflectionRoughnessThreshold

    object.Settings.bOverride_LocalExposureDetailStrength = true
    object.Settings.LocalExposureDetailStrength = config["AutoExposure"].ExposureDetailStrength

    object.Settings.AutoExposureBias = exposureBias
    object.Settings.LocalExposureHighlightContrastScale = 0.78
    object.Settings.LocalExposureShadowContrastScale = shadowContrast
end

function ResetExteriorSettings(object)
    object.Settings.bOverride_LumenSkylightLeaking = true

    object.Settings.bOverride_LumenDiffuseColorBoost = true
    object.Settings.LumenDiffuseColorBoost = 1.2

    object.Settings.AmbientOcclusionIntensity = 0.5
    object.Settings.AmbientOcclusionRadius = 150.0
    object.Settings.AmbientOcclusionPower = 3.0

    object.Settings.bOverride_BloomIntensity = true
    object.Settings.BloomIntensity = 3.7

    object.Settings.bOverride_LumenReflectionMaxRoughnessToTrace = true
    object.Settings.LumenReflectionMaxRoughnessToTrace = 0.4

    object.Settings.bOverride_LocalExposureDetailStrength = true
    object.Settings.LocalExposureDetailStrength = 1.2

    object.Settings.AutoExposureBias = 0.0
    object.Settings.LocalExposureHighlightContrastScale = 0.7
    object.Settings.LocalExposureShadowContrastScale = 0.7
end

function SetInteriorSettings(object)
    if (config["General"].Enabled == false) then
        ResetInteriorSettings(object)
        return
    end

    local environmentName = object:GetFullName()
    local exposureBias = config["AutoExposure"].InteriorBias
    local exposureDungeonOffset = config["AutoExposure"].DungeonOffset
    local shadowContrast = config["AutoExposure"].InteriorShadowContrast

    if string.find(environmentName, "Crypt") or
            string.find(environmentName, "Mine") or
            string.find(environmentName, "Cave") or
            string.find(environmentName, "Ruin") or
            string.find(environmentName, "Temple")
    then
        exposureBias = exposureBias + exposureDungeonOffset
    end

    object.Settings.bOverride_LumenSkylightLeaking = true
    object.Settings.LumenSkylightLeaking = 0.326

    object.Settings.bOverride_LumenDiffuseColorBoost = true
    object.Settings.LumenDiffuseColorBoost = 3.8

    object.Settings.bOverride_BloomIntensity = true
    object.Settings.BloomIntensity = config["General"].BloomIntensity

    object.Settings.bOverride_LumenReflectionMaxRoughnessToTrace = true
    object.Settings.LumenReflectionMaxRoughnessToTrace = config["General"].ReflectionRoughnessThreshold

    object.Settings.bOverride_LocalExposureDetailStrength = true
    object.Settings.LocalExposureDetailStrength = config["AutoExposure"].ExposureDetailStrength

    object.Settings.AutoExposureBias = exposureBias
    object.Settings.AutoExposureMinBrightness = -5.0
    object.Settings.AutoExposureMaxBrightness = 20.0
    object.Settings.LocalExposureHighlightContrastScale = 0.88
    object.Settings.LocalExposureShadowContrastScale = shadowContrast
end

function ResetInteriorSettings(object)
    object.Settings.bOverride_LumenSkylightLeaking = true
    object.Settings.LumenSkylightLeaking = 0.7

    object.Settings.bOverride_LumenDiffuseColorBoost = true
    object.Settings.LumenDiffuseColorBoost = 1.7

    object.Settings.bOverride_LocalExposureDetailStrength = true
    object.Settings.LocalExposureDetailStrength = 1.2

    object.Settings.bOverride_BloomIntensity = true
    object.Settings.BloomIntensity = 3.7

    object.Settings.bOverride_LumenReflectionMaxRoughnessToTrace = true
    object.Settings.LumenReflectionMaxRoughnessToTrace = 0.4

    object.Settings.AutoExposureBias = 0.0
    object.Settings.AutoExposureMinBrightness = -10.0
    object.Settings.AutoExposureMaxBrightness = 5.0
    object.Settings.LocalExposureHighlightContrastScale = 0.7
    object.Settings.LocalExposureShadowContrastScale = 0.7
end

function SetExteriorWhiteBalance(object)
    if (config["General"].Enabled == false) or (config["ColorCorrection"].Enabled == false) then
        ResetExteriorWhiteBalance(object)
        return
    end

    object.Settings.bOverride_BlueCorrection = true
    object.Settings.BlueCorrection = config["ColorCorrection"].ExteriorBlueCorrection

    object.Settings.bOverride_WhiteTemp = true

    if (ksl:GetConsoleVariableBoolValue("r.Lumen.HardwareRayTracing") == false) then
        object.Settings.WhiteTemp = config["ColorCorrection"].ExteriorWhiteBalance - 400
        return
    end

    object.Settings.WhiteTemp = config["ColorCorrection"].ExteriorWhiteBalance
end

function ResetExteriorWhiteBalance(object)
    object.Settings.bOverride_BlueCorrection = true
    object.Settings.BlueCorrection = 0.8

    object.Settings.bOverride_WhiteTemp = true
    object.Settings.WhiteTemp = 6500
end

function SetInteriorWhiteBalance(object)
    if (config["General"].Enabled == false) or (config["ColorCorrection"].Enabled == false) then
        ResetInteriorWhiteBalance(object)
        return
    end

    object.Settings.bOverride_WhiteTemp = true
    object.Settings.WhiteTemp = config["ColorCorrection"].InteriorWhiteBalance
end

function ResetInteriorWhiteBalance(object)
    object.Settings.bOverride_WhiteTemp = true
    object.Settings.WhiteTemp = 6500
end

function SetSkylightIntensity()
    if (config["General"].Enabled == false) then
        ResetSkyLightIntensity()
        return
    end

    if (ksl:GetConsoleVariableBoolValue("r.Lumen.HardwareRayTracing") == false) then
        ExecuteInGameThread(function()
            ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 0.52", nil)
        end)

        ExecuteWithDelay(1, function()
            ExecuteInGameThread(function()
                ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 0.52", nil)
            end)
        end)
        return
    end

    ExecuteInGameThread(function()
        ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 0.78", nil)
    end)

    ExecuteWithDelay(1, function()
        ExecuteInGameThread(function()
            ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 0.78", nil)
        end)
    end)
end

function ResetSkyLightIntensity()
    ExecuteInGameThread(function()
        ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 1.0", nil)
    end)

    ExecuteWithDelay(1, function()
        ExecuteInGameThread(function()
            ksl:ExecuteConsoleCommand(engine, "r.SkylightIntensityMultiplier 1.0", nil)
        end)
    end)
end

function SetColorCorrection(object)
    if (config["General"].Enabled == false) or (config["ColorCorrection"].Enabled == false) then
        ResetColorCorrection(object)
        return
    end

    object.Settings.bOverride_ColorSaturation = true
    object.Settings.bOverride_ColorContrast = true
    object.Settings.bOverride_ColorOffset = true

    object.Settings.ColorSaturation.X = config["ColorCorrection"].ColorSaturationX
    object.Settings.ColorSaturation.Y = config["ColorCorrection"].ColorSaturationY
    object.Settings.ColorSaturation.Z = config["ColorCorrection"].ColorSaturationZ
    object.Settings.ColorSaturation.W = config["ColorCorrection"].ColorSaturationW
    object.Settings.ColorContrast.X = config["ColorCorrection"].ColorContrastX
    object.Settings.ColorContrast.Y = config["ColorCorrection"].ColorContrastY
    object.Settings.ColorContrast.Z = config["ColorCorrection"].ColorContrastZ
    object.Settings.ColorContrast.W = config["ColorCorrection"].ColorContrastW
    object.Settings.ColorOffset.X = config["ColorCorrection"].ColorOffsetX
    object.Settings.ColorOffset.Y = config["ColorCorrection"].ColorOffsetY
    object.Settings.ColorOffset.Z = config["ColorCorrection"].ColorOffsetZ
    object.Settings.ColorOffset.W = config["ColorCorrection"].ColorOffsetW
end

function ResetColorCorrection(object)
    object.Settings.bOverride_ColorSaturation = false
    object.Settings.bOverride_ColorContrast = false
    object.Settings.bOverride_ColorOffset = false

    object.Settings.ColorSaturation.X = 1.0
    object.Settings.ColorSaturation.Y = 1.0
    object.Settings.ColorSaturation.Z = 1.0
    object.Settings.ColorSaturation.W = 1.0
    object.Settings.ColorContrast.X = 1.0
    object.Settings.ColorContrast.Y = 1.0
    object.Settings.ColorContrast.Z = 1.0
    object.Settings.ColorContrast.W = 1.0
    object.Settings.ColorOffset.X = 0.0
    object.Settings.ColorOffset.Y = 0.0
    object.Settings.ColorOffset.Z = 0.0
    object.Settings.ColorOffset.W = 0.0
end

function SetSkyAtmosphereSettings(object)
    if (config["General"].Enabled == false) then
        ResetSkyAtmosphereSettings(object)
        return
    end

    object.RayleighExponentialDistribution = config["General"].RayleighExponentialDistribution
end

function ResetSkyAtmosphereSettings(object)
    object.RayleighExponentialDistribution = 8.0
end