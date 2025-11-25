from phone_app.tools import dev2pjsip_vol, pjsip2dev_vol


def test_volume_in():
    assert pjsip2dev_vol(0) == 0
    assert dev2pjsip_vol(0) == 0

    assert pjsip2dev_vol(0.5) == 25
    assert dev2pjsip_vol(25) == 0.5

    assert pjsip2dev_vol(1.0) == 50
    assert dev2pjsip_vol(50) == 1.0

    assert pjsip2dev_vol(1.5) == 75
    assert dev2pjsip_vol(75) == 1.5

    assert pjsip2dev_vol(2.0) == 100
    assert dev2pjsip_vol(100) == 2.0
