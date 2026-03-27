UEHelpers = require('UEHelpers')
engine = FindFirstOf('Engine')
GetKismetSystemLibrary = UEHelpers.GetKismetSystemLibrary
ksl = GetKismetSystemLibrary()

local function execCmd(cmd)
    local pc = UEHelpers.GetPlayerController()
    pcall(function() ksl:ExecuteConsoleCommand(engine, cmd, pc, false) end)
end

NotifyOnNewObject("/Script/Altar.AltarCommonGameViewportClient", function(viewPort)
    execCmd("r.SkyAtmosphere.TransmittanceLUT 0")
    execCmd("r.MotionBlur.TargetFPS 0")
    execCmd("r.MotionBlur.Scale 0.5")
    execCmd("r.Lumen.SampleFog 1")
    execCmd("r.NGX.DLSS.AutoExposure 1")
    execCmd("r.EyeAdaptation.MethodOverride 2")
    execCmd("r.VolumetricFog.Emissive 0")
    execCmd("r.LightMaxDrawDistanceScale 2")
end)

NotifyOnNewObject("/Script/Engine.PostProcessVolume", function(object)
    object.Settings.bOverride_LumenFrontLayerTranslucencyReflections = false
    object.Settings.LumenFrontLayerTranslucencyReflections = 1

    object.Settings.bOverride_LumenSkylightLeaking = false
    object.Settings.LumenSkylightLeaking = 0.1

    object.Settings.bOverride_LumenDiffuseColorBoost = false
    object.Settings.LumenDiffuseColorBoost = 4.0
    
    object.Settings.bOverride_WhiteTemp = false
    object.Settings.WhiteTemp = 5500

    object.Settings.bOverride_WhiteTint = false
    object.Settings.WhiteTint = -0.1
end)

NotifyOnNewObject("/Script/Engine.PostProcessComponent", function(object)
    object.Settings.bOverride_LumenFrontLayerTranslucencyReflections = true
    object.Settings.LumenFrontLayerTranslucencyReflections = 1

    object.Settings.bOverride_LumenSkylightLeaking = true
    object.Settings.LumenSkylightLeaking = 0.1

    object.Settings.bOverride_LumenDiffuseColorBoost = true
    object.Settings.LumenDiffuseColorBoost = 4.0
    
    object.Settings.bOverride_WhiteTemp = true
    object.Settings.WhiteTemp = 5500

    object.Settings.bOverride_WhiteTint = true
    object.Settings.WhiteTint = -0.1
end)