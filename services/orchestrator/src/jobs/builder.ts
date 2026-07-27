import { randomUUID } from 'crypto';

export interface ProjectContext {
  context_id: string;
  metadata: { project_id: string; workflow: string };
  brand: any;
  art_direction: any;
  characters: any[];
  environments: any[];
}

export function buildJobs(creativePlan: any): { projectContext: ProjectContext, jobs: any[] } {
  const artDir = creativePlan.art_direction || {};
  const brand = creativePlan.brand_identity || {};
  const env = creativePlan.environment || {};
  const cinema = creativePlan.cinematography || {};
  const voicePlan = creativePlan.voice_plan || {};
  const musicPlan = creativePlan.music_plan || {};
  const characters = creativePlan.characters?.character_sheets || [];
  const locations = env.locations || [];
  
  const projectId = creativePlan.project?.project_id || `proj_${randomUUID().substring(0, 8)}`;
  const traceId = `trace_${randomUUID().substring(0, 12)}`;
  const contextId = `ctx_${randomUUID().substring(0, 8)}`;

  const projectContext: ProjectContext = {
    context_id: contextId,
    metadata: { project_id: projectId, workflow: "v4.2" },
    brand: {
      brand_id: "brand_001",
      colors: brand.color_palette || [],
      logo_rules: brand.logo_rules || "",
      personality: brand.brand_personality || ""
    },
    art_direction: {
      visual_style: artDir.visual_style || "Cinematic",
      camera_type: artDir.camera_type || "Digital Cinema Camera",
      lens: artDir.lens || "35mm",
      color_grading: artDir.color_grading || "Natural",
      aspect_ratio: cinema.aspect_ratio || "16:9"
    },
    characters: characters.map((c: any, i: number) => ({
      character_id: `char_${i+1}`,
      name: c.name || "",
      appearance: c.appearance || {},
      outfits: c.outfits || []
    })),
    environments: locations.map((loc: any, i: number) => ({
      environment_id: `env_${i+1}`,
      name: typeof loc === 'string' ? loc : (loc.name || ""),
      architecture: typeof loc === 'string' ? "" : (loc.architecture || ""),
      weather: typeof loc === 'string' ? "" : (loc.weather || ""),
      lighting: typeof loc === 'string' ? "" : (loc.lighting || ""),
      time_of_day: typeof loc === 'string' ? "" : (loc.time_of_day || ""),
      props: typeof loc === 'string' ? [] : (loc.key_props || [])
    }))
  };

  const references = {
    character: projectContext.characters.length ? projectContext.characters[0].character_id : "char_001",
    environment: projectContext.environments.length ? projectContext.environments[0].environment_id : "env_001",
    brand: projectContext.brand.brand_id
  };

  const allJobs: any[] = [];
  const promptPack = creativePlan.prompt_pack || {};
  const scenes = promptPack.scenes || [];
  let jobCounter = 1;

  for (const scene of scenes) {
    const sceneId = scene.scene_id || 1;
    const shots = scene.shots || [];

    // Music Job (Per Scene)
    if (Object.keys(musicPlan).length > 0) {
      allJobs.push({
        job_id: `music_scene_${sceneId}`,
        idempotency_key: `music_scene_${sceneId}`,
        queue: "music-generation",
        priority: 70,
        trace: { trace_id: traceId, parent_job: `scene_${sceneId}` },
        provider: { name: "Suno", model: "v3", version: "3.0", api_version: "2026-02" },
        generation: {
          genre: musicPlan.genre || "",
          mood: musicPlan.mood || "",
          instruments: musicPlan.instruments || [],
          tempo: musicPlan.tempo || "90 BPM",
          duration: 30
        },
        references,
        dependencies: [],
        input_assets: [],
        failure_policy: { on_failure: "retry", max_attempts: 3, fallback_provider: "BackupProvider" },
        callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
        output: { asset_id: `music_scene_${sceneId}`, version: 1, bucket: "creative-assets", path: `${projectId}/audio/music_scene_${sceneId}.mp3`, format: "mp3" },
        metadata: { project_id: projectId, scene_id: sceneId, workflow: "v4.2" }
      });
    }

    for (const shot of shots) {
      const shotId = shot.shot_id || `S${jobCounter}`;
      const rawDependsOn = shot.depends_on || [];
      const dependencies = rawDependsOn.map((dep: string) => ({ job: dep, type: "required" }));
      const inputAssets = rawDependsOn
        .filter((dep: string) => dep.toLowerCase().includes("img") || dep.toLowerCase().includes("image"))
        .map((dep: string) => ({ asset_id: dep, type: "image" }));

      // Images
      const images = shot.images || [];
      images.forEach((img: any, idx: number) => {
        const jobId = `img_${shotId}_${idx+1}`;
        allJobs.push({
          job_id: jobId,
          idempotency_key: jobId,
          queue: "image-generation",
          priority: 90,
          trace: { trace_id: traceId, parent_job: `scene_${sceneId}` },
          provider: { name: "Flux", model: img.model || "flux-pro", version: "1.1", api_version: "2026-05" },
          prompt: img.prompt || "",
          negative_prompt: img.negative_prompt || "",
          generation: { seed: img.seed || 1001, cfg: 7.5, steps: 30, sampler: "DPM++", scheduler: "Karras", width: 1920, height: 1080 },
          references,
          reference_assets: [{ asset_id: references.environment, weight: 0.8 }],
          dependencies: [],
          input_assets: [],
          failure_policy: { on_failure: "retry", max_attempts: 3, fallback_provider: "SDXL" },
          callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
          output: { asset_id: jobId, version: 1, bucket: "creative-assets", path: `${projectId}/images/${jobId}.png`, format: "png" },
          metadata: { project_id: projectId, scene_id: sceneId, shot_id: shotId, workflow: "v4.2" }
        });
      });

      // Videos
      const videos = shot.videos || [];
      videos.forEach((vid: any, idx: number) => {
        const jobId = `vid_${shotId}_${idx+1}`;
        allJobs.push({
          job_id: jobId,
          idempotency_key: jobId,
          queue: "video-generation",
          priority: 85,
          trace: { trace_id: traceId, parent_job: `scene_${sceneId}` },
          provider: { name: "Google", model: "Veo 3", version: "1.0", api_version: "2026-06" },
          prompt: vid.prompt || "",
          generation: { camera_motion: vid.camera_motion || "Static", duration: vid.duration || 4, fps: 24, resolution: "1080p" },
          references,
          dependencies,
          input_assets: inputAssets,
          failure_policy: { on_failure: "retry", max_attempts: 2, fallback_provider: "Sora" },
          callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
          output: { asset_id: jobId, version: 1, bucket: "creative-assets", path: `${projectId}/videos/${jobId}.mp4`, format: "mp4" },
          metadata: { project_id: projectId, scene_id: sceneId, shot_id: shotId, workflow: "v4.2" }
        });
      });

      // Voice
      if (shot.voice) {
        const jobId = `voice_${shotId}`;
        allJobs.push({
          job_id: jobId,
          idempotency_key: jobId,
          queue: "voice-generation",
          priority: 80,
          trace: { trace_id: traceId, parent_job: `scene_${sceneId}` },
          provider: { name: "ElevenLabs", model: "eleven_multilingual_v2", version: "2.0", api_version: "2026-01" },
          text: shot.voice.text || "",
          generation: { voice: shot.voice.voice || voicePlan.gender || "Neutral", emotion: shot.voice.emotion || voicePlan.emotion || "Friendly", pace: voicePlan.pace || "Medium" },
          references,
          dependencies: [],
          input_assets: [],
          failure_policy: { on_failure: "retry", max_attempts: 3, fallback_provider: "BackupProvider" },
          callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
          output: { asset_id: jobId, version: 1, bucket: "creative-assets", path: `${projectId}/audio/${jobId}.wav`, format: "wav" },
          metadata: { project_id: projectId, scene_id: sceneId, shot_id: shotId, workflow: "v4.2" }
        });
      }

      // SFX
      const sfxs = shot.sfx || [];
      sfxs.forEach((sfx: any, idx: number) => {
        const jobId = `sfx_${shotId}_${idx+1}`;
        allJobs.push({
          job_id: jobId,
          idempotency_key: jobId,
          queue: "sfx-generation",
          priority: 60,
          trace: { trace_id: traceId, parent_job: `scene_${sceneId}` },
          provider: { name: "ElevenLabs SFX", model: "eleven_sfx_v1", version: "1.0", api_version: "2026-03" },
          generation: { effect: sfx.effect || "" },
          references,
          dependencies,
          input_assets: inputAssets,
          failure_policy: { on_failure: "retry", max_attempts: 3, fallback_provider: "BackupProvider" },
          callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
          output: { asset_id: jobId, version: 1, bucket: "creative-assets", path: `${projectId}/audio/${jobId}.wav`, format: "wav" },
          metadata: { project_id: projectId, scene_id: sceneId, shot_id: shotId, workflow: "v4.2" }
        });
      });

      jobCounter++;
    }
  }

  // Final Composition / Stitching Job (FFmpeg Editor)
  const allVideoDependencies = allJobs
    .filter(job => job.queue === 'video-generation' || job.queue === 'voice-generation' || job.queue === 'music-generation')
    .map(job => ({ job: job.job_id, type: 'required' }));

  const allVideoAssets = allJobs
    .filter(job => job.queue === 'video-generation' || job.queue === 'voice-generation' || job.queue === 'music-generation')
    .map(job => ({ asset_id: job.job_id, type: job.queue.split('-')[0] }));

  // Build the Edit Decision List (EDL) so FFmpeg knows the exact timeline
  const edl: any[] = [];
  let currentTime = 0;
  
  for (const scene of scenes) {
    for (const shot of (scene.shots || [])) {
      const durationStr = shot.duration || "4s";
      const durationSec = parseInt(durationStr.replace(/\D/g, '')) || 4; // Extract seconds (e.g., "4s" -> 4)
      
      const shotVideos = allJobs.filter(j => j.queue === 'video-generation' && j.metadata.shot_id === shot.shot_id);
      
      if (shotVideos.length > 0) {
        // Add the video clip to the timeline
        edl.push({
          type: "video_clip",
          asset_id: shotVideos[0].job_id,
          start_time: currentTime,
          end_time: currentTime + durationSec,
          transition: shot.transition || "cut"
        });
        
        // Add associated voiceover if exists
        const shotVoice = allJobs.filter(j => j.queue === 'voice-generation' && j.metadata.shot_id === shot.shot_id);
        if (shotVoice.length > 0) {
          edl.push({
            type: "audio_voice",
            asset_id: shotVoice[0].job_id,
            start_time: currentTime,
            volume: 1.0
          });
        }
      }
      currentTime += durationSec;
    }
  }

  // Add the master music track across the whole timeline
  const musicJob = allJobs.find(j => j.queue === 'music-generation');
  if (musicJob) {
    edl.push({
      type: "audio_music",
      asset_id: musicJob.job_id,
      start_time: 0,
      end_time: currentTime,
      volume: 0.2 // Background music level
    });
  }

  allJobs.push({
    job_id: `master_composition_${projectId}`,
    idempotency_key: `master_composition_${projectId}`,
    queue: "video-composition", // Picked up by the Editing Worker (e.g., using FFmpeg)
    priority: 100, // Highest priority, runs last
    trace: { trace_id: traceId, parent_job: `project_${projectId}` },
    provider: { name: "FFmpeg Worker", model: "standard", version: "1.0", api_version: "2026-07" },
    generation: { 
      resolution: "1080p", 
      fps: 24, 
      format: "mp4",
      timeline_edl: edl // <--- The FFmpeg Blueprint!
    },
    references,
    dependencies: allVideoDependencies, // MUST wait for ALL video, voice, and music jobs to finish!
    input_assets: allVideoAssets, // Passes the Redis/S3 locations of every single clip to FFmpeg!
    failure_policy: { on_failure: "retry", max_attempts: 2, fallback_provider: "none" },
    callback: { type: "rabbitmq", events: ["generation.started", "generation.progress", "generation.completed", "generation.failed", "generation.cancelled"] },
    output: { asset_id: `final_master`, version: 1, bucket: "creative-assets", path: `${projectId}/master/final_ad.mp4`, format: "mp4" },
    metadata: { project_id: projectId, workflow: "v4.2" }
  });

  return { projectContext, jobs: allJobs };
}
