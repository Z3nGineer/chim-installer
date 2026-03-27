-- Eternal Darkness - Immersive Nights and Dungeons VERSION: v.0.89a
print("[Eternal Darkness] Starting up…")

-- ============================================================================
-- USER-CONFIGURABLE SECTION
-- ============================================================================

-- Toggle to enable or disable outdoor night effects (moon/skylight dimming and fog adjustments). 
-- Set this to false if you want the exterior world to retain its default night lighting.
local ENABLE_OUTDOOR_NIGHT = true

-- Start and end hours for "night" (0–23). Default is 21–5. (If you want 21:30 set it to 21.5)
local NIGHT_START_HOUR = 21
local NIGHT_END_HOUR   = 5

-- List of interior names where fog volumes should be removed completely. (Full darkness)
-- The name must match the segment after "L_" and before "_Li" in the level instance name: 
-- L_FortHomestead02_Li -> "FortHomestead02").
local FOG_REMOVAL_LEVELS = {
    FortHomestead02 = true,
	SerpentsTrail = true,
	ShadowsRestCavern02 = true,
	-- Example: MyDungeon01 = true,
}

-- Optional global fog removal categories.
-- If true, all matching interior types will have fog removed automatically. (Full darkness)
local REMOVE_FOG_IN_ALL_CAVES = false
local REMOVE_FOG_IN_ALL_MINES = false
local REMOVE_FOG_IN_ALL_FORTS = false
local REMOVE_FOG_IN_ALL_SEWER = false

-- Include additional worlds for night effect.
local NIGHT_WORLD_TAGS = {
    "L_Tamriel",          -- base world
    -- Add more world names if needed (ToDo: SI)
}

-- Adjust these values to fine-tune the brightness of various light sources.

-- Fort interiors:
local BRAZIER_PIT_INTENSITY   = 800.0
local BRAZIER_HALL_INTENSITY  = 300.0
local BRAZIER_HALL2_INTENSITY = 900.0
local BRAZIER_HALL3_INTENSITY = 900.0
local CAMPFIRE_FORT_INTENSITY = 950.0

-- Cave interiors:
local CAMPFIRE_CAVE_INTENSITY     = 850.0
local CAMPFIRE_INTENSITY 		  = 800.0
local TORCH_GOBLIN_CAVE_INTENSITY = 850.0
local TORCH_TALL01_INTENSITY 	  = 850.0
local CANDLE_FAT02_INTENSITY 	  = 15.0
local CANDLE_FAT03_INTENSITY 	  = 20.0

-- Mine interiors:
local MINE_SPOTLIGHT_INTENSITY = 1.0

-- Ayleid interiors:
local CANDLE_LINE_LARGE_INTENSITY     = 10.0
local CANDLE_DRESSING_SMALL_INTENSITY = 5.0
local WELKYD_CLUSTER_WHITE_INTENSITY  = 790.0

-- Sewer interiors:
local SEWER_SPOTLIGHT_INTENSITY  = 15.0

-- Oblivion Gate interiors:
local OBLIVION_CAVE_POINTLIGHT_INTENSITY = 50.0
local OBLIVION_CAVE_SPOTLIGHT_INTENSITY  = 20.0

-- Other interiors:
local IMPERIAL_DUNGEON_SPOTLIGHT_INTENSITY = 30.0

-- Spot light dimming:
local CAVE_SPOTLIGHT_BRIGHTNESS  = 0.85
local OTHER_SPOTLIGHT_BRIGHTNESS = 0.75

-- ============================================================================
-- END USER-CONFIGURABLE SECTION
-- ============================================================================

-- === Interior Control ===

-- ToDo User Configs
local REMOVE_NIGHT_FOG = true
local DISABLE_MOONLIGHT = false
local DISABLE_SKYLIGHT  = true
-- Custom dimming: 0.0 = pitch black, 1.0 = vanilla bright, 0.4 = nice middle ground
local DIM_MOONLIGHT = true
local MOONLIGHT_INTENSITY = 0.7
local DIM_SKYLIGHT = true
local SKYLIGHT_INTENSITY = 0.3

-- Cached reference to the ATMSubsystem.
local gATMSubsystem = CreateInvalidObject()

-- Returns the current game hour (0–23) by querying the ATMSubsystem.
function getGameTimeHour()
    if not gATMSubsystem:IsValid() then
        gATMSubsystem = FindFirstOf("ATMSubsystem")
    end
    if gATMSubsystem and gATMSubsystem:IsValid() then
        local gameTime = gATMSubsystem:GetTime()
        if gameTime then
            return math.floor(gameTime) % 24
        end
    end
    return nil
end

-- Determine if the world belongs to one of the "night" worlds. 
local function isNightWorld(name)
    if not name then return false end
    local lower = string.lower(name)

    -- Always allow Tamriel world
    if string.find(lower, "/game/maps/world/l_tamriel") then
        return true
    end

    -- Handle temporary worldlighting levels (Imperial City districts, etc.)
    if string.find(lower, "/temp/game/maps/world/l_worldlighting_levelinstance_") then
        return true
    end

    -- Fallback user-specified tags
    for _, tag in ipairs(NIGHT_WORLD_TAGS) do
        if string.find(lower, string.lower(tag), 1, true) then
            return true
        end
    end

    return false
end


-- Returns true if the string contains the interior map prefix.
local function isInterior(fullName)
    return fullName and string.find(fullName, "/Game/Maps/Interiors/") ~= nil
end

-- Process all point lights currently in memory.
local function processPointLights()
    local pointLights = FindAllOf("PointLightComponent")
    if not pointLights then return end
    for _, light in ipairs(pointLights) do
        if light and light:IsValid() then
            local ok, fullName = pcall(function() return light:GetFullName() end)
            if ok and fullName and isInterior(fullName) then

                -- Light Sources
                if string.find(fullName, "BP_RFPitColumnShortBrazier01_C") then
                    pcall(function() light:SetIntensity(BRAZIER_PIT_INTENSITY) end)
					
                elseif string.find(fullName, "BP_RFHallWFireBrazier01_C") then
                    pcall(function() light:SetIntensity(BRAZIER_HALL_INTENSITY) end)
					
				elseif string.find(fullName, "BP_RFHallWFireBrazier02_C") then
                    pcall(function() light:SetIntensity(BRAZIER_HALL2_INTENSITY) end)
					
				elseif string.find(fullName, "BP_RFHallWFireBrazier03_C") then
                    pcall(function() light:SetIntensity(BRAZIER_HALL3_INTENSITY) end)
					
				elseif string.find(fullName, "BP_RFPitBridgeBrazier02Ash_C") then
                    pcall(function() light:SetIntensity(BRAZIER_HALL2_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(400) end)
										
				elseif string.find(fullName, "BP_PF_Campfire_Fort_Sta_C") then
                    pcall(function() light:SetIntensity(CAMPFIRE_FORT_INTENSITY) end)
					
				elseif string.find(fullName, "BP_PF_Campfire_Cave_Sta_C") then
                    pcall(function() light:SetIntensity(CAMPFIRE_CAVE_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(500) end)	
				
				elseif string.find(fullName, "BP_PF_Campfire_C") then
                    pcall(function() light:SetIntensity(CAMPFIRE_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(500) end)
					
				elseif string.find(fullName, "BP_PF_Campfire_Mine_Sta_C") then
                    pcall(function() light:SetIntensity(CAMPFIRE_FORT_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)	
					
				elseif string.find(fullName, "Campfire_Sewer_Sta_C_0") then
                    pcall(function() light:SetIntensity(500) end)	
					
				elseif string.find(fullName, "BP_PF_Torch_GoblinCave_C") then
                    pcall(function() light:SetIntensity(TORCH_GOBLIN_CAVE_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)
				
				elseif string.find(fullName, "BP_TorchTall01_C") then
                    pcall(function() light:SetIntensity(TORCH_GOBLIN_CAVE_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)
								
				elseif string.find(fullName, "BP_PF_Torchtall01_Sta_C") then
                    pcall(function() light:SetIntensity(TORCH_TALL01_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)
					
				elseif string.find(fullName, "BP_PF_Torch02_Sta_C") then
                    pcall(function() light:SetIntensity(TORCH_TALL01_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)
					
				elseif string.find(fullName, "VActivable_") then
                    pcall(function() light:SetIntensity(TORCH_TALL01_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)						
				
				elseif string.find(fullName, "BP_SkullOnAStick01_C") then
                    pcall(function() light:SetIntensity(TORCH_TALL01_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(300) end)		
				
				elseif string.find(fullName, "BP_PF_Candle_Fat02_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT02_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)
				
				elseif string.find(fullName, "BP_CandleFatEvil03Fake_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT02_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)		

				elseif string.find(fullName, "BP_PF_CandleDressing_Small_04_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT02_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)	
					
				elseif string.find(fullName, "BP_PF_CandleDressing_Corner_Inner_Medium_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT03_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)		

				elseif string.find(fullName, "BP_PF_CandleDressing_Line_Large_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_LINE_LARGE_INTENSITY) end)
				
				elseif string.find(fullName, "BP_PF_CandleDressing_Corner_Inner_Medium_C") then
                    pcall(function() light:SetIntensity(CANDLE_LINE_LARGE_INTENSITY) end)
					
				elseif string.find(fullName, "BP_PF_CandleFatEvil01_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_LINE_LARGE_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)

				elseif string.find(fullName, "BP_PF_CandleDressing_Small_01_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_DRESSING_SMALL_INTENSITY) end)
				
				elseif string.find(fullName, "BP_PF_CandleDressing_Small_03_C") then
                    pcall(function() light:SetIntensity(CANDLE_DRESSING_SMALL_INTENSITY) end)
					
				elseif string.find(fullName, "BP_PF_CandleDressing_Small_04_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT02_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)
					
				elseif string.find(fullName, "BP_PF_CandleDressing_Small_03_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT03_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)
					
				elseif string.find(fullName, "BP_PF_CandleDressing_Small_02_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_FAT02_INTENSITY) end)
					pcall(function() light:SetAttenuationRadius(170) end)
					
				elseif string.find(fullName, "BP_PF_CandleDressing_Line_Medium_C") then
                    pcall(function() light:SetIntensity(CANDLE_DRESSING_SMALL_INTENSITY) end)
				
				elseif string.find(fullName, "BP_PF_CandleDressing_Line_Medium_Sta_C") then
                    pcall(function() light:SetIntensity(CANDLE_DRESSING_SMALL_INTENSITY) end)
					
				elseif string.find(fullName, "BP_PF_BurnPile_C") then
                    pcall(function() light:SetIntensity(1200) end)
					pcall(function() light:SetAttenuationRadius(700) end)
					
				elseif string.find(fullName, "BP_PF_Burntrubblepile01_Sta_C") then
                    pcall(function() light:SetIntensity(3000) end)
					pcall(function() light:SetAttenuationRadius(800) end)
					
				elseif string.find(fullName, "BP_Brazier01_C") then
                    pcall(function() light:SetIntensity(900) end)
					pcall(function() light:SetAttenuationRadius(800) end)
								
				elseif string.find(fullName, "BP_ARWelkydClusterWhite01_C") then
                    pcall(function() light:SetIntensity(WELKYD_CLUSTER_WHITE_INTENSITY) end)
				

				-- Add more ...
								
                -- Generic point lights (brightened for visibility)
                elseif string.match(fullName, "%.PointLight_%d+") then
                    -- skip: leave generic point lights at vanilla intensity
                end
				
				-- Special cases:
				local lower = string.lower(fullName)
				
                -- Special case for Memorial Cave: 
                if string.find(lower, "memorial_cave") then
                    if string.match(fullName, "%.PointLight_0%.LightComponent0$") or
                       string.match(fullName, "%.PointLight_2%.LightComponent0$") or
                       string.match(fullName, "%.PointLight_5%.LightComponent0$") then
                        pcall(function() light:SetIntensity(950.0) end)
						pcall(function() light:SetAttenuationRadius(400) end)
                    end
                end

				-- Special case for Lord Drads Estate:
				if string.find(lower, "lorddradsestatefarm") then
                    if string.match(fullName, "%.PointLight_0%.LightComponent0$") then
                        pcall(function() light:SetIntensity(30.0) end)
                    end
                end
					
				-- Special case for Oblivion Sigil Towers: 
				if string.find(lower, "oblivionrd001citadel_") or 
				   string.find(lower, "oblivionrd002citadel_") or 
				   string.find(lower, "oblivionrd003citadel_") or
				   string.find(lower, "oblivionrd004citadel_") or 
				   string.find(lower, "oblivionrd005citadel_") or
				   string.find(lower, "oblivionrd006citadel_") or
				   string.find(lower, "oblivionrdcitadel01_") or
				   string.find(lower, "oblivionrdcitadel02_") or
				   string.find(lower, "oblivionrdcitadel03_") or 
				   string.find(lower, "oblivionrdcitadel04_") or
				   string.find(lower, "oblivionrdcitadel05_") or
				   string.find(lower, "oblivionrdcitadel06_") then
				   
                    if string.match(fullName, "%.PointLight_0%.LightComponent0$") then
                        pcall(function() light:SetIntensity(350000.000000) end)

					elseif string.match(fullName, "%.PointLight_1%.LightComponent0$") then
                        pcall(function() light:SetIntensity(250000.000000) end)
						
					elseif string.match(fullName, "%.PointLight_2%.LightComponent0$") or
                           string.match(fullName, "%.PointLight_3%.LightComponent0$") or
                           string.match(fullName, "%.PointLight_4%.LightComponent0$") or
                           string.match(fullName, "%.PointLight_5%.LightComponent0$") or
                           string.match(fullName, "%.PointLight_6%.LightComponent0$") then
                        pcall(function() light:SetIntensity(150000.000000) end)	
						
                    end
                end
				
				if string.find(lower, "oblivionrdcitadel01lord_") or 
				   string.find(lower, "oblivionrdcitadel02lord_") or 
				   string.find(lower, "oblivionrdcitadel03lord_") or 
				   string.find(lower, "oblivionrdcitadel04lord_") or
				   string.find(lower, "oblivionrdcitadel05lord_") or
				   string.find(lower, "oblivionrd001citadellord_") or
				   string.find(lower, "oblivionrd002citadellord_") or
				   string.find(lower, "oblivionrd003citadellord_") or
				   string.find(lower, "oblivionrd004citadellord_") or
				   string.find(lower, "oblivionrd005citadellord_") or
				   string.find(lower, "oblivionrd006citadellord_") or
				   string.find(lower, "oblivionrdcitadel06lord_") then
				   
                    if string.match(fullName, "%.PointLight_0%.LightComponent0$") then
                        pcall(function() light:SetIntensity(70) end)
                    end
                end
			
            end
        end
    end
end

-- Fog adjustments for specific dungeons
local function processSpecialDungeonFog()
    local fogComps = FindAllOf("ExponentialHeightFogComponent")
    if fogComps then
        for _, fog in ipairs(fogComps) do
            if fog and fog:IsValid() then
                local okFog, fogName = pcall(function() return fog:GetFullName() end)
                if okFog and fogName then
                    local lowerName = string.lower(fogName)
                    -- Bleak Flats Cave: dense fog and volumetric distance
                    if string.find(lowerName, "bleakflatscave") then
                        pcall(function()
                            if fog:IsValid() then
                                fog:SetVolumetricFogDistance(1000)
                                fog:SetFogDensity(1.0)
                            end
                        end)
                    elseif string.find(lowerName, "beldaburo") then
                        -- Special case (Beldaburo)
                        pcall(function()
                            if fog:IsValid() then
                                fog:SetVolumetricFogDistance(0)
                                fog:SetFogDensity(0.0)
                            end
                        end)
                    end
                end
            end
        end
    end
end

-- Process all spot lights currently in memory.
local function processSpotLights()
    local spotLights = FindAllOf("SpotLight")
    if not spotLights then return end
    for _, actor in ipairs(spotLights) do
        if actor and actor:IsValid() then
            local ok, fullName = pcall(function() return actor:GetFullName() end)
            if ok and fullName and isInterior(fullName) then
                if string.match(fullName, "%.SpotLight_%d+") then
                    -- For any cave interior (case-insensitive "cave" in the path), dim spotlights.
					-- For any mine interior (case-insensitive "mine" in the path), dim spotlights.
                    -- Otherwise disable generic spotlights.
                    local lowerName = string.lower(fullName)
                    if string.find(lowerName, "cave") then
                        pcall(function() actor:SetBrightness(CAVE_SPOTLIGHT_BRIGHTNESS) end)
                    elseif string.find(lowerName, "mine") then
                        pcall(function() actor:SetBrightness(MINE_SPOTLIGHT_INTENSITY) end)
                    else
						pcall(function() actor:SetBrightness(OTHER_SPOTLIGHT_BRIGHTNESS) end)
                    end
                end
            end
        end
    end
end

-- Finds all SpotLightComponent instances whose full path includes "sewer".
local function processSewerSpotLights()
    local comps = FindAllOf("SpotLightComponent")
    if not comps then return end
    for _, comp in ipairs(comps) do
        if comp and comp:IsValid() then
            local ok, fullName = pcall(function() return comp:GetFullName() end)
            if ok and fullName then
                local lowerName = string.lower(fullName)
                if string.find(lowerName, "sewer") then
                    local intensity

                    -- Disable specular components
                    if string.find(lowerName, "bp_pf_specular") then
                        intensity = 0.0

                    -- Only touch spotlight components ending in .LightComponent0
                    elseif string.match(fullName, "%.SpotLight_%d+%.LightComponent0$") then
                        -- Start with the default sewer intensity
                        intensity = SEWER_SPOTLIGHT_INTENSITY

                        -- ImperialSewers03 overrides
                        if string.find(lowerName, "imperialsewers03") then
                            if string.match(fullName, "%.SpotLight_0%.LightComponent0$") or
                               string.match(fullName, "%.SpotLight_1%.LightComponent0$") or
                               string.match(fullName, "%.SpotLight_4%.LightComponent0$") then
                                intensity = 0.0
                            elseif string.match(fullName, "%.SpotLight_12%.LightComponent0$") then
                                intensity = 10000000.0
                            end
                        end
                    end

                    -- Apply intensity only if we set a value
                    if intensity then
                        pcall(function() comp:SetIntensity(intensity) end)
                    end
                end
            end
        end
    end
	
	-- 2) Hide or show volumetric light cylinders and fog sheets.
    local staticMeshes = FindAllOf("StaticMeshComponent")
    if staticMeshes then
        for _, sm in ipairs(staticMeshes) do
            if sm and sm:IsValid() then
                local ok, fullName = pcall(function() return sm:GetFullName() end)
                if ok and fullName then
                    local lowerName = string.lower(fullName)
                    if string.find(lowerName, "sewer") then
                        if string.find(lowerName, "bp_volumetric_lightfog_cylinder_c") or
                           string.find(lowerName, "bp_fogsheet_c") then
                            pcall(function() sm:SetHiddenInGame(true, true) end)
                        end
                    end
                end
            end
        end
    end
	
	-- 3) Hide or show god ray actors and their associated meshes.
    local godRayActors = FindAllOf("BP_GodRay_C")
    if godRayActors then
        for _, actor in ipairs(godRayActors) do
            if actor and actor:IsValid() then
                local ok, fullName = pcall(function() return actor:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") then
                    -- Hide the actor at night; show it during the day
                    pcall(function() actor:SetActorHiddenInGame(true) end)
                end
            end
        end
    end
    local billboards = FindAllOf("BillboardComponent")
    if billboards then
        for _, bb in ipairs(billboards) do
            if bb and bb:IsValid() then
                local ok, fullName = pcall(function() return bb:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") and
                   string.find(fullName, ".UISprite") then
                    pcall(function() bb:SetVisibility(false, true) end)
                end
            end
        end
    end
	
	-- 4) Hide or show volumetric light fog actors themselves.
    local fogActors = FindAllOf("BP_Volumetric_LightFog_Cylinder_C")
    if fogActors then
        for _, actor in ipairs(fogActors) do
            if actor and actor:IsValid() then
                local ok, fullName = pcall(function() return actor:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") then
                    pcall(function() actor:SetActorHiddenInGame(true) end)
                end
            end
        end
    end	
end

-- Update Sewer Lights
local function updateSewerLightVisibility()
    local hour = getGameTimeHour()
    if not hour then return end

    local isNight = (hour >= NIGHT_START_HOUR) or (hour < NIGHT_END_HOUR)
    local defaultSewerIntensity = SEWER_SPOTLIGHT_INTENSITY

    -- 1) Adjust light intensity for sewer light components.
    local function setSewerComponentIntensity(className)
		local comps = FindAllOf(className)
		if not comps then return end
		for _, comp in ipairs(comps) do
			if comp and comp:IsValid() then
				local ok, fullName = pcall(function() return comp:GetFullName() end)
				if ok and fullName then
					local lowerName = string.lower(fullName)
					if string.find(lowerName, "sewer") then
						-- Skip ImperialSewers03 spotlight 12 entirely; its intensity is set in processSewerSpotLights().
						if string.find(lowerName, "imperialsewers03") and
						   string.match(lowerName, "%.spotlight_12%.lightcomponent0$") then
							-- Do nothing: leave whatever intensity was set earlier.
						else
							local intensity = isNight and 0.0 or defaultSewerIntensity
							pcall(function() comp:SetIntensity(intensity) end)
						end
					end
				end
			end
		end
	end
	setSewerComponentIntensity("SpotLightComponent")
	setSewerComponentIntensity("PointLightComponent")

    -- 2) Hide or show volumetric light cylinders and fog sheets.
    local staticMeshes = FindAllOf("StaticMeshComponent")
    if staticMeshes then
        for _, sm in ipairs(staticMeshes) do
            if sm and sm:IsValid() then
                local ok, fullName = pcall(function() return sm:GetFullName() end)
                if ok and fullName then
                    local lowerName = string.lower(fullName)
                    if string.find(lowerName, "sewer") then
                        if string.find(lowerName, "bp_volumetric_lightfog_cylinder_c") or
                           string.find(lowerName, "bp_fogsheet_c") then
                            pcall(function() sm:SetHiddenInGame(isNight, true) end)
                        end
                    end
                end
            end
        end
    end

    -- 3) Hide or show god ray actors and their associated meshes.
    local godRayActors = FindAllOf("BP_GodRay_C")
    if godRayActors then
        for _, actor in ipairs(godRayActors) do
            if actor and actor:IsValid() then
                local ok, fullName = pcall(function() return actor:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") then
                    -- Hide the actor at night; show it during the day
                    pcall(function() actor:SetActorHiddenInGame(isNight) end)
                end
            end
        end
    end
    local billboards = FindAllOf("BillboardComponent")
    if billboards then
        for _, bb in ipairs(billboards) do
            if bb and bb:IsValid() then
                local ok, fullName = pcall(function() return bb:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") and
                   string.find(fullName, ".UISprite") then
                    pcall(function() bb:SetVisibility(not isNight, true) end)
                end
            end
        end
    end

    -- 4) Hide or show volumetric light fog actors themselves.
    local fogActors = FindAllOf("BP_Volumetric_LightFog_Cylinder_C")
    if fogActors then
        for _, actor in ipairs(fogActors) do
            if actor and actor:IsValid() then
                local ok, fullName = pcall(function() return actor:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), "sewer") then
                    pcall(function() actor:SetActorHiddenInGame(isNight) end)
                end
            end
        end
    end

    -- Reschedule this check to run again every 60 seconds.
    ExecuteWithDelay(60000, updateSewerLightVisibility)
end

-- === Imperial Dungeon Control ===
local function processImperialDungeonLights()
    -- Identify any ImperialDungeon map
    local dungeonTag = "imperialdungeon"

    -- Zero out all point lights in Imperial Dungeons
    local points = FindAllOf("PointLightComponent")
    if points then
        for _, comp in ipairs(points) do
            if comp and comp:IsValid() then
                local ok, fullName = pcall(function() return comp:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), dungeonTag) then
                    pcall(function() comp:SetIntensity(0.0) end)
                end
            end
        end
    end

    -- Set all spotlights in Imperial Dungeons to 30.0
    local spots = FindAllOf("SpotLightComponent")
    if spots then
        for _, comp in ipairs(spots) do
            if comp and comp:IsValid() then
                local ok, fullName = pcall(function() return comp:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), dungeonTag) then
                    -- Only adjust the LightComponent0 on spotlights to avoid altering other child components
                    if string.match(fullName, "%.SpotLight_%d+%.LightComponent0$") then
                        pcall(function() comp:SetIntensity(IMPERIAL_DUNGEON_SPOTLIGHT_INTENSITY) end)
                    end
                end
            end
        end
    end
	
	-- Hide Imperial Dungeon skylight components
	local skylights = FindAllOf("SkyLightComponent")
    if skylights then
        for _, sl in ipairs(skylights) do
            if sl and sl:IsValid() then
                local ok, fullName = pcall(function() return sl:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), dungeonTag) then
                    -- Hide skylights
                    pcall(function() sl:SetVisibility(false, true) end)
                end
            end
        end
    end
end

-- Process Oblivion Plane (RD Cave) lights
local function processOblivionRDCaveLights()
    local caveTag = "oblivionrdcave"
    local points = FindAllOf("PointLightComponent")
    if points then
        for _, comp in ipairs(points) do
            if comp and comp:IsValid() then
                local ok, fullName = pcall(function() return comp:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), caveTag) then
                    pcall(function() comp:SetIntensity(OBLIVION_CAVE_POINTLIGHT_INTENSITY) end)
                end
            end
        end
    end
    local spots = FindAllOf("SpotLightComponent")
    if spots then
        for _, comp in ipairs(spots) do
            if comp and comp:IsValid() then
                local ok, fullName = pcall(function() return comp:GetFullName() end)
                if ok and fullName and string.find(string.lower(fullName), caveTag) then
                    if string.match(fullName, "%.SpotLight_%d+%.LightComponent0$") then
                        pcall(function() comp:SetIntensity(OBLIVION_CAVE_SPOTLIGHT_INTENSITY) end)
                    end
                end
            end
        end
    end
end

-- Hide skylights in all interiors
local function processSkyLights()
    -- Disabled: hiding interior skylights made interiors too dark
    -- UltraPlusExtensions skylight profile handles interior dimming instead
end

-- Remove volumetric fog meshes in selected interiors or global categories.
local function processFogMeshes()
    local meshes = FindAllOf("StaticMeshComponent")
    if not meshes then return end

    for _, mesh in ipairs(meshes) do
        if mesh and mesh:IsValid() then
            local ok, name = pcall(function() return mesh:GetFullName() end)
            if ok and name and isInterior(name) then
                -- Extract the interior name (like "FortHomestead02" from "L_FortHomestead02_Li")
                local interiorName = string.match(name, "L_([%w]+)%_Li")

                local shouldRemoveFog = false

                -- Direct table match
                if interiorName and FOG_REMOVAL_LEVELS[interiorName] then
                    shouldRemoveFog = true
                end

                -- Global fog-removal categories
                local lower = string.lower(name)
                if not shouldRemoveFog then
                    if REMOVE_FOG_IN_ALL_CAVES and string.find(lower, "cave") then
                        shouldRemoveFog = true
                    elseif REMOVE_FOG_IN_ALL_MINES and string.find(lower, "mine") then
                        shouldRemoveFog = true
                    elseif REMOVE_FOG_IN_ALL_FORTS and string.find(lower, "fort") then
                        shouldRemoveFog = true
					elseif REMOVE_FOG_IN_ALL_SEWER and string.find(lower, "sewer") then
                        shouldRemoveFog = true
                    end
                end

                -- Hide volumetric fog meshes if eligible
                if shouldRemoveFog and string.find(name, ".VolumeMesh") then
                    if string.find(name, "BP_Volumetric_GlobalFog") or
                       string.find(name, "BP_Volumetric_GroundFog_C_") then
                        pcall(function() mesh:SetVisibility(false, true) end)
                    end
                end
            end
        end
    end
end

-- === Exterior Control ===

-- Cached reference to the ATMSubsystem.
local gATMSubsystem = CreateInvalidObject()

-- Returns the current game hour (0–23) by querying the ATMSubsystem.
local function getGameTimeHour()
    if not gATMSubsystem:IsValid() then
        gATMSubsystem = FindFirstOf("ATMSubsystem")
    end
    if gATMSubsystem and gATMSubsystem:IsValid() then
        local gameTime = gATMSubsystem:GetTime()
        if gameTime then
            return math.floor(gameTime) % 24
        end
    end
    return nil
end

-- True when a Night Eye status effect actor is present
local function isNightEyeActive()
    local effects = FindAllOf("BPCI_StatusEffect_NightEyes_C")
    if effects then
        for _, effect in ipairs(effects) do
            if effect and effect:IsValid() then
                -- Read the IsFinished boolean; if it exists and is false, Night Eye is active
                local ok, finished = pcall(function() return effect.IsFinished end)
                if ok and finished == false then
                    return true
                end
            end
        end
    end
    return false
end

-- Updates visibility of the directional moon and skylight.
local function updateWorldLights()
	-- Skip exterior night adjustments if disabled in the user config
    if not ENABLE_OUTDOOR_NIGHT then
        return
    end
	
    local hour = getGameTimeHour()
    if hour ~= nil then
        local isNight = (hour >= NIGHT_START_HOUR) or (hour < NIGHT_END_HOUR)
		
		if isNight and isNightEyeActive() then
            isNight = false  -- treat night as day while NightEye effect is active
        end	
        -- Iterate over all directional light components and hide/show those that match the Night World moon pattern.
        local dirComps = FindAllOf("DirectionalLightComponent")
        if dirComps then
            for _, dl in ipairs(dirComps) do
                if dl and dl:IsValid() then
                    local ok, fname = pcall(function() return dl:GetFullName() end)
                    if ok and fname then
                        -- Only affect lights in the world/Tamriel map with a moon suffix
                        if isNightWorld(fname) and string.find(fname, ".DirectionalLight_Moon") then
							if DISABLE_MOONLIGHT then
								pcall(function() dl:SetVisibility(not isNight, true) end)
							elseif DIM_MOONLIGHT and isNight then
								pcall(function()
									local lightComp = dl.LightComponent
									if lightComp and lightComp:IsValid() then
										lightComp:SetIntensity(lightComp:GetIntensity() * MOONLIGHT_INTENSITY)
									end
								end)
							end
                        end
                    end
                end
            end
        end
        -- Iterate over skylight actors and hide/show those in the Night World.
        local skyActors = FindAllOf("SkyLight")
        if skyActors then
            for _, sa in ipairs(skyActors) do
                if sa and sa:IsValid() then
                    local ok, fname = pcall(function() return sa:GetFullName() end)
                    if ok and fname then
                        if isNightWorld(fname) then
							if DISABLE_SKYLIGHT then
								pcall(function() sa:SetActorHiddenInGame(isNight) end)
							elseif DIM_SKYLIGHT and isNight then
								pcall(function()
									local lightComp = sa.LightComponent
									if lightComp and lightComp:IsValid() then
										lightComp:SetIntensity(lightComp:GetIntensity() * SKYLIGHT_INTENSITY)
									end
								end)
							end
                        end
                    end
                end
            end
        end
    end
	
    -- Reschedule this check to run again after 20 seconds (20000 ms)
    ExecuteWithDelay(20000, updateWorldLights)
end

-- Module-level variable to track whether we last adjusted fog during night or day
local lastFogNightState = nil  

-- Periodically adjusts the Exponential Height Fog distance.
local function adjustFogDistance()
    if not ENABLE_OUTDOOR_NIGHT then
        return
    end

    local hour = getGameTimeHour()
    if hour ~= nil then
        -- Determine if it's night based on user-configurable start/end
        local isNight = (hour >= NIGHT_START_HOUR) or (hour < NIGHT_END_HOUR)

        -- If Night Eye is active, treat it as day
        if isNight and isNightEyeActive() then
            isNight = false
        end

        -- Always apply night fog values every cycle if it's night,
        -- but only apply day values if we are transitioning from night to day.
        local shouldUpdateFog = false
        if isNight then
            shouldUpdateFog = true
            lastFogNightState = true
        else
            -- If we just switched from night to day, update; otherwise leave fog unchanged.
            if lastFogNightState then
                shouldUpdateFog = true
            end
            lastFogNightState = false
        end

        if shouldUpdateFog and REMOVE_NIGHT_FOG then
            local distance = isNight and 500000 or 0
            local fogComps = FindAllOf("ExponentialHeightFogComponent")
            if fogComps then
                for _, fog in ipairs(fogComps) do
                    if fog and fog:IsValid() then
                        local okName, fogName = pcall(function() return fog:GetFullName() end)
                        if okName and fogName and isNightWorld(fogName) then
                            pcall(function()
                                ExecuteInGameThread(function()
                                    if fog:IsValid() then
                                        -- During the night: force volumetric fog updates and set custom distance.
                                        if isNight then
                                            for _ = 1, 3 do
                                                pcall(function() fog:SetVolumetricFog(true) end)
                                                pcall(function() fog:SetVolumetricFog(false) end)
                                            end
                                            pcall(function() fog:SetVolumetricFog(true) end)
                                            pcall(function() fog:SetComponentTickEnabled(false) end)
                                            pcall(function() fog:SetVolumetricFogDistance(500000) end)
                                            pcall(function() fog:SetStartDistance(500000) end)

                                            local darkAlbedo  = { R = 0.05, G = 0.05, B = 0.05, A = 1.0 }
                                            local moonColor   = { R = 0.10, G = 0.10, B = 0.20, A = 1.0 }
                                            pcall(function() fog:SetVolumetricFogAlbedo(darkAlbedo) end)
                                            pcall(function() fog:SetDirectionalInscatteringColor(moonColor) end)
                                        else
                                            -- During the day: restore default values only once.
                                            pcall(function() fog:SetComponentTickEnabled(true) end)
                                            pcall(function() fog:SetVolumetricFog(true) end)
                                            pcall(function() fog:SetVolumetricFogDistance(0) end)
                                            pcall(function() fog:SetStartDistance(0) end)

                                            local defaultAlbedo  = { R = 1.0, G = 1.0, B = 1.0, A = 1.0 }
                                            local defaultDirCol = { R = 0.25, G = 0.25, B = 0.125, A = 1.0 }
                                            pcall(function() fog:SetVolumetricFogAlbedo(defaultAlbedo) end)
                                            pcall(function() fog:SetDirectionalInscatteringColor(defaultDirCol) end)
                                        end
                                    end
                                end)
                            end)
                        end
                    end
                end
            end
        end
    end

    -- Schedule the next fog adjustment in 10000 ms (10 seconds).
    ExecuteWithDelay(10000, adjustFogDistance)
end

-- === Execution Control ===

-- Runs all interior lighting and fog adjustments.
local function adjustAll()
    processPointLights()
    processSpotLights()
	processSewerSpotLights() 
	processImperialDungeonLights()
	processOblivionRDCaveLights() 
    processSkyLights()
    processFogMeshes()
	processSpecialDungeonFog()
end

-- Schedules a one-time light scan after the level finishes loading.
local function scheduleLightScan(delay)
    local ms = delay or 1000
    ExecuteWithDelay(ms, function()
        adjustAll()
    end)
end

-- Hook into the Altar level-change event.
local function setupHooks()
    -- Initial pass after startup
    scheduleLightScan(2000)
    -- Subsequent passes on each level load
    RegisterHook("/Script/Altar.VLevelChangeData:OnFadeToGameBeginEventReceived", function()
        scheduleLightScan(1000)
		-- Immediately update exterior darkening and fog when a new level finishes loading
		ExecuteWithDelay(500, function()
            updateWorldLights()    -- apply moon/sky darkening right away
            adjustFogDistance()    -- adjust exterior fog distance right away      
        end)
    end)
end

-- Setting up hooks.
local function init()
	-- Startup Interior
    setupHooks()
	updateSewerLightVisibility()
	-- Startup Exterior
	updateWorldLights()
	adjustFogDistance()
end

init()

print("[Dark Nights & Dungeons] Initialised.")