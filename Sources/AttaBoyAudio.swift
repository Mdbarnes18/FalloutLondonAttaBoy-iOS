import AVFoundation

@MainActor
final class AttaBoyAudio {
    static let shared = AttaBoyAudio()
    private var player: AVAudioPlayer?

    private init() {}

    func play(_ sound: String) {
        guard let url = Bundle.main.url(forResource: sound, withExtension: "wav") else { return }
        do {
            player = try AVAudioPlayer(contentsOf: url)
            player?.prepareToPlay()
            player?.play()
        } catch {
            // Sound is optional feedback; playback failure must never interrupt game actions.
        }
    }
}
