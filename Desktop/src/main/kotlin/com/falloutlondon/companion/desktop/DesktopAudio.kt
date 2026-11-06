package com.falloutlondon.companion.desktop

import java.io.BufferedInputStream
import java.util.concurrent.ConcurrentHashMap
import javax.sound.sampled.AudioSystem
import javax.sound.sampled.Clip
import javax.sound.sampled.LineEvent

object DesktopAudio {
    private val activeClips = ConcurrentHashMap<String, Clip>()

    fun play(name: String) {
        runCatching {
            val resource = Thread.currentThread().contextClassLoader
                .getResourceAsStream("assets/atta-boy/audio/pack_$name.wav") ?: return
            val audio = AudioSystem.getAudioInputStream(BufferedInputStream(resource))
            val clip = AudioSystem.getClip()
            clip.open(audio)
            audio.close()
            activeClips[name]?.close()
            activeClips[name] = clip
            clip.addLineListener { event ->
                if (event.type == LineEvent.Type.STOP) {
                    clip.close()
                    activeClips.remove(name, clip)
                }
            }
            clip.start()
        }
    }
}
