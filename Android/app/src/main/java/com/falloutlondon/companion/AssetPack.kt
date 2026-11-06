package com.falloutlondon.companion

import android.content.Context
import android.media.MediaPlayer
import androidx.compose.foundation.Image
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource

private val PackPhosphor = Color(0xFF00FF44)

/** Loads one of the namespaced vector assets imported from the complete asset pack. */
@Composable
fun PackAssetIcon(name: String, modifier: Modifier = Modifier, contentDescription: String? = null) {
    val context = LocalContext.current
    val resourceId = remember(name, context.packageName) {
        context.resources.getIdentifier("pack_" + name, "drawable", context.packageName)
    }
    if (resourceId != 0) {
        Image(
            painter = painterResource(resourceId),
            contentDescription = contentDescription,
            modifier = modifier,
            colorFilter = ColorFilter.tint(PackPhosphor)
        )
    }
}

/** Plays a bundled pack sound and releases the decoder as soon as playback finishes. */
fun playPackSound(context: Context, name: String) {
    val resourceId = context.resources.getIdentifier("pack_" + name, "raw", context.packageName)
    if (resourceId == 0) return
    MediaPlayer.create(context, resourceId)?.also { player ->
        player.setOnCompletionListener { it.release() }
        player.setOnErrorListener { mediaPlayer, _, _ -> mediaPlayer.release(); true }
        player.start()
    }
}
